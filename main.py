
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

from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session

DATABASE_URL="sqlite:///./livros.db"

engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

app=FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros.",
    version="1.0.0",
    contact={
        "name":"Ciro Da Rocha",
        "email":"cirocincinato1@gmail.com"
    }
)

MEU_USUARIO="a"
MINHA_SENHA="a"

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




















#paginação somente no meto GET
@app.get("/livros")
def get_livros(page: int=1,limit:int=10,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
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
    





















    
# id do livro
# nome do livro
# autor do livro
# ano de lançamento do livro    
@app.post("/adiciona")
def post_livros(livro:Livro,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    db_livro=db.query(LivroDB).filter(LivroDB.nome_livro==livro.nome_livro,LivroDB.autor_livro==livro.autor_livro).first()
    if db_livro:
        raise HTTPException(status_code=400, detail="esse livro ja existe no banco de dados")
    novo_livro=LivroDB(nome_livro=livro.nome_livro,autor_livro=livro.autor_livro,ano_livro=livro.ano_livro)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)
    return{"message":"o livro foi criado com sucesso"}
#precisamos atualizar a informação especificando quem é com id_livro
#1.quem é o livro(id_livro)
#2.pegar o livro(id_livro)
#3.atualização de informações do livro
#dicionário=HashMap
#cahve->valor
#meu_livro está recebendo meus_livrozinhos.get(id_livro)
#isso cria uma referencia antiga e por consequncia quando tentamos atualizar com meu_livro[id_livro]=livro.dict()
#isso atualiza a informçaõ em um id de referencia o que gera o problema onde as atualização 
# apartir de uma terceira vez avera parcialemnte atualização correta porem sempre vai ter as informaçoes do meus_livrozinhos antiga
#quando utilizamos meus_livrozinhos[id_livro]=livro.dict() estamos mudando a informaçaõ no dicionario atual e não em uam referncia 
#




















@app.put("/atualiza/{id_livro}")
def put_livro(id_livro:int,livro:Livro,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
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
def delete_livro(id_livro:int,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):    
    db_livro=db.query(LivroDB).filter(LivroDB.id==id_livro).first()
    if not db_livro:
        raise HTTPException(status_code=404,detail="este livro nao foi encontrado")
    db.delete(db_livro)
    db.commit()
    return {"message":"seu livro foi deletado."}
#ACIND
#ORM ->OBJECT Relational Mapping
