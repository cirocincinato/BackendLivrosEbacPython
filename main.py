from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os
import redis
import json
from fastapi import BackgroundTasks
from tasks import somar,fatorial
from celery_app import celery_app
from celery.result import AsyncResult
from sqlalchemy import create_engine,Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
import asyncio
from kafka_producer import enviar_evento

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL=os.getenv("DATABASE_URL")

engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

REDIS_HOST=os.getenv("REDIS_HOST","localhost")
REDIS_PORT=os.getenv("REDIS_PORT","6379")
redis_client=redis.Redis(host=REDIS_HOST,port=REDIS_PORT, db=0, decode_responses=True)

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
#meus_livrozinhos={}

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
@app.get("/")
def hello_world():
    return {"Hello":"World!"}

def autenticar_meu_usuario(credentials:HTTPBasicCredentials=Depends(security)):
    is_username_correct=secrets.compare_digest(credentials.username,MEU_USUARIO)
    is_password_correct=secrets.compare_digest(credentials.password,MINHA_SENHA)

    if not(is_username_correct and is_password_correct):
        raise HTTPException(status_code=401, detail="usuário ou senha incorretos", headers={"WWW-Authenticate":"Basic"})
@app.post("/calcular/soma")
def calcular_soma(a:int,b:int):
    tarefa=somar.delay(a,b)
    redis_client.lpush("tarefas_ids",tarefa.id)
    redis_client.ltrim("tarefas_ids",0,49)
    return{
        "task_id":tarefa.id,
        "message":"Tarefa de soma envida"
    }
@app.post("/calcular/fatorial")
def calcular_fatorial(n:int):
    tarefa=fatorial.delay(n)
    redis_client.lpush("tarefas_ids",tarefa.id)
    redis_client.ltrim("tarefas_ids",0,49)
    return{
        "task_id":tarefa.id,
        "message":"Tarefa de fatorial envida"
    }
    

@app.get("/tarefas/recentes")
def listar_tarefas_recentes():
    ids= redis_client.lrange("tarefas_ids",0,-1)
    tarefas=[]
    for task_id in ids:
        resultado=AsyncResult(task_id,app=celery_app)
        tarefas.append({
            "task_id":task_id,
            "status":resultado.status,
            "resultado":resultado.result if resultado.successful() else None
        })
    return {"tarefas":tarefas}

@app.get("/calcular/status/{task_id}")
def status_tarefa(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    status = result.status
    resposta = {"task_id": task_id, "status": status}

    if status in ("SUCCESS", "FAILURE"):
        # Se terminou (com sucesso ou erro), removemos o id do Redis
        redis_client.lrem("tarefas_ids", 0, task_id)
        resposta["result"] = result.result  # Mostra o resultado ou exceção

    return resposta

#estrategia de cache para pegar POST,PUT,DELET da api
@app.get("/debug/redis")    
def ver_livros_redis():
    chaves=redis_client.keys("livros:*")
    livros=[]
    for chave in chaves:
        valor=redis_client.get(chave)  
        ttl=redis_client.ttl(chave)
        livros.append({"chave":chave,"valor":json.loads(valor),"TTL":ttl})      
    return livros

@app.get("/livros")
async def get_livros(page: int=1,limit:int=100,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    if page < 0 or limit<=0:
        raise HTTPException(status_code=400,detail="page ou limit estão com valores inválidos!!")
    
    
    cache_key=f"livros:page={page}&limit={limit}"
    cached=redis_client.get(cache_key)

    if cached:
        print("cached")
        return json.loads(cached)

    livros=db.query(LivroDB).offset((page-1)*limit).limit(limit).all()
    if not livros:
        return {"message":"Não existe nenhum livro!!"}

    
    total_livros=db.query(LivroDB).count()
    resposta= {
        "page":page, 
        "limit":limit,
        "total":total_livros,
        "livros":[{"id":livro.id,"nome_livro":livro.nome_livro,"autor_livro":livro.autor_livro,"ano_livro":livro.ano_livro}
                  for livro in livros]
    }
    redis_client.setex(cache_key,30,json.dumps(resposta))
    return resposta

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

    enviar_evento("livros_eventos",{
        "acao":"criar",
        "livro":livro.dict()
    })
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
    salvar_livro_redis(db_livro.id,livro)
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
