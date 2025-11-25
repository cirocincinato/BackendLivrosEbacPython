
#API de livros

#GET, POST,PUT,DELETE

#POST - Adicionar novos livros(create)
#GET - buscar os dados dos livros(read)
#PUT - Atualizar informações dos livros(update)
#DELETE - Deletar informações dps livros(delete)

#CRUDE é =

#create
#read
#update
#delete

# Vamos acessar nosso ENDPOINT -->http://127.0.0.1:8000
# E vamos acessar os PATH's desse endpoint-->/adiciona
# -->?id_livro=1&nome_livro=ciro rei persa&autor_livro=ciro&ano_livro=2025

#final exemplo usando o POST -->http://127.0.0.1:8000/adiciona?id_livro=1&nome_livro=ciro%20rei%20persa&autor_livro=ciro&ano_livro=2025

#documentação Swagger -> documentar os endpoints da nossa aplicação(da nossa API)

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os
import redis
import json

from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session

import asyncio

DATABASE_URL=os.getenv("DATABASE_URL")

engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

redis_client=redis.Redis(host='localhost',port=6379, db=0, decode_responses=True)

app=FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros.",
    version="1.0.0",
    contact={
        "name":"Ciro Da Rocha",
        "email":"cirocincinato1@gmail.com"
    }
)

MEU_USUARIO=os.getenv("MEU_USUARIO")
MINHA_SENHA=os.getenv("MINHA_SENHA")

security=HTTPBasic()
meus_livrozinhos={}

#POO:hernça sendo passada. essa clase ajuda a definir o formato das informáções
#assim o proximo passo é ajustar todos os metos para que se 
# adapitem há essa classe:class Livros(BaseModel):
class LivroDB(Base):
    __tablename__="Livros"
    id=Column(Integer,primary_key=True,index=True)
    nome_livro=Column(String , index=True)
    autor_livro=Column(String,index=True)
    ano_livro=Column(Integer)

class Livro(BaseModel):
    nome_livro:str
    autor_livro:str
    ano_livro:int

Base.metadata.create_all(bind=engine)

def salvar_livro_redis(livro_id: int, livro: Livro):
    
    redis_client.set(f"livro:{livro_id}", json.dumps(livro.dict()))

def deletar_livro_redis(livro_id:int):
    redis_client.delete(f"livro:{livro_id}")


def sessao_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


def autenticar_meu_usuario(credentials:HTTPBasicCredentials=Depends(security)):
    is_username_correct=secrets.compare_digest(credentials.username,MEU_USUARIO)
    is_password_correct=secrets.compare_digest(credentials.password,MINHA_SENHA)

    if not(is_username_correct and is_password_correct):
        raise HTTPException(status_code=401, detail="usuário ou senha incorretos", headers={"WWW-Authenticate":"Basic"})
'''   
async def chamada_externa_1():
    await asyncio.sleep(3)
    return "resultado chamda externa 1"
async def chamada_externa_2():
    await asyncio.sleep(2)
    return "resultado chamda externa 2"
async def chamada_externa_3():
    await asyncio.sleep(1)
    return "resultado chamda externa 3"
@app.get("/chamadas-externas")
async def chamdas_externas():
    tarefa1=asyncio.create_task(chamada_externa_1())
    tarefa2=asyncio.create_task(chamada_externa_2())
    tarefa3=asyncio.create_task(chamada_externa_3())
    resultado1=await tarefa1
    resultado2=await tarefa2
    resultado3=await tarefa3
    return {"mesagem":"todas as chamadas nas API`s foram concluidas com sucesso",
            "resultado":[resultado1,resultado2,resultado3]}
''' 
@app.get("debug/redis")    
def ver_livros_redis():
    chaves=redis_client.keys("livros:*")
    livros=[]
    for chave in chaves:
        valor=redis_client.get(chave)  
        livros.append({"chave":chave,"valor":json.loads(valor)})      
    return livros
#paginação somente no meto GET
@app.get("/livros")
async def get_livros(page: int=1,limit:int=100,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    if page < 0 or limit<=0:
        raise HTTPException(status_code=400,detail="page ou limit estão com valores inválidos!!")
    
    livros=db.query(LivroDB).offset((page-1)*limit).limit(limit).all()

    if not livros:
        return {"message":"Não existe nenhum livro!!"}

    #livro_paginados=[
    #    {"id":id_livro, "nome_livro":livro_data["nome_livro"],"autor_livro":livro_data["autor_livro"],"ano_livro":livro_data["ano_livro"]}
    #    for id_livro,livro_data in livros_ordenados [start:end] 
    #]
    total_livros=db.query(LivroDB).count()
    return {
        "page":page, 
        "limit":limit,
        "total":total_livros,
        "livros":[{"id":livro.id,"nome_livro":livro.nome_livro,"autor_livro":livro.autor_livro,"ano_livro":livro.ano_livro}
                  for livro in livros]
    }
  
@app.post("/adiciona") 
async def post_livros(livro:Livro,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    db_livro=db.query(LivroDB).filter(LivroDB.nome_livro==livro.nome_livro,LivroDB.autor_livro==livro.autor_livro).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="esse livro ja existe no banco de dados")
    novo_livro=LivroDB(nome_livro=livro.nome_livro,autor_livro=livro.autor_livro,ano_livro=livro.ano_livro)
    db.add(novo_livro)
    db.commit() 
    db.refresh(novo_livro)
    salvar_livro_redis(novo_livro.id,livro)
    return{"message":"o livro foi criado com sucesso"}

@app.put("/atualiza/{id_livro}")
async def put_livro(id_livro:int,livro:Livro,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    db_livro=db.query(LivroDB).filter(LivroDB.id==id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=400,detail="livro nao existe dentro do banco de dados!")
    
    db_livro.nome_livro=livro.nome_livro
    db_livro.autor_livro=livro.autor_livro
    db_livro.ano_livro=livro.ano_livro

    db.commit()
    db.refresh(db_livro)
    return{"message":"livro atualizado com sucesso"}


@app.delete("/deletar/{id_livro}")
async def delete_livro(id_livro:int,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):    
    db_livro=db.query(LivroDB).filter(LivroDB.id==id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404,detail="este livro nao foi encontrado")
    db.delete(db_livro)
    db.commit()
    deletar_livro_redis(id_livro)
    return {"message":"seu livro foi deletado."}
#ACIND
#ORM ->OBJECT Relational Mapping
