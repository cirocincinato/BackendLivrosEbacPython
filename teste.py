from typing import Optional
from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials 
#importação do Modelo com Pydantic
from pydantic import BaseModel
import secrets
import os

from sqlalchemy import create_engine,Column,Integer,String, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.exc import IntegrityError
DATABASE_URL="sqlite:///./tarefas.db"

engine=create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

app=FastAPI(
    title="projeto de tarefas sendo feito novamente",
    description="primeira vercao basica"
)

class TarefaDB(Base):
    __tablename__="Tarefa"
    id=Column(Integer,primary_key=True,index=True)
    nome=Column(String,  index=True, unique=True, nullable=False)
    descricao=Column(String,  index=True, nullable=False)
    concluida=Column(Boolean, nullable=False, default=False)

class Tarefa(BaseModel):
    nome:str
    descricao:str
    concluida:bool=False
class TarefaConcluida(BaseModel):
    nome:str

Base.metadata.create_all(bind=engine)

def sessao_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

EU="a"
SENHA="a"
security=HTTPBasic()
def autentica(credentials:HTTPBasicCredentials=Depends(security)):
    usuario_correto=secrets.compare_digest(credentials.username,EU)
    senha_correta=secrets.compare_digest(credentials.password,SENHA)
    if not(usuario_correto and senha_correta):
        raise HTTPException(status_code=401,detail="usuario ou senha incoretos",headers={"WWW-Authenticate":"Basic"})

@app.post("/tarefas/adicionar", status_code=201)
def post_tarefa(tarefa:Tarefa,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autentica)):
    nome = tarefa.nome.strip()
    desc = tarefa.descricao.strip()
    if not nome:
        raise HTTPException(status_code=400,detail="nome é obrigatório!")
    if not desc:
        raise HTTPException(status_code=400,detail="descrição é obrigatório!")
    db_tarefa=db.query(TarefaDB).filter(TarefaDB.nome==nome).first()
    if db_tarefa:
        raise HTTPException(status_code=409, detail="essa tarefa ja existe no banco de dados!")
    nova_tarefa=TarefaDB(nome=nome,descricao=desc,concluida=tarefa.concluida)
    db.add(nova_tarefa)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Se outra request inseriu o mesmo nome nesse intervalo
        raise HTTPException(status_code=409, detail="essa tarefa já existe no banco de dados!")

    db.refresh(nova_tarefa)
    return {
    "id": nova_tarefa.id,
    "nome": nova_tarefa.nome,
    "descricao": nova_tarefa.descricao,
    "concluida": nova_tarefa.concluida,
    }

@app.get("/tarefas/mostrar", status_code=200)
def get_tarefas(page:int=1, limit:int=1,order: str = "asc", 
    order_por: str = "id",  db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autentica)):
    if page<1 or limit<=0:
        raise HTTPException(status_code=400, detail="page ou limit inválidos!")
    direction = order.lower()
    if direction not in ("asc", "desc"):
        raise HTTPException(status_code=400, detail="order deve ser 'asc' ou 'desc'")
    reverse = (direction == "desc")

    campo = order_por.lower()
    # mapeia o parâmetro para a coluna do ORM
    colunas = {
        "id": TarefaDB.id,
        "nome": TarefaDB.nome,
        "descricao": TarefaDB.descricao,
        "concluida": TarefaDB.concluida,
    }
    if campo not in colunas:
        raise HTTPException(status_code=400, detail="order_por deve ser 'id', 'nome', 'descricao' ou 'concluida'")

    col = colunas[campo]

    # monta query ordenada antes de paginar
    q = db.query(TarefaDB)
    q = q.order_by(col.desc() if reverse else col.asc())

    total = q.count()
    itens = q.offset((page - 1) * limit).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "tarefas": [
            {"id": t.id, "nome": t.nome, "descricao": t.descricao, "concluida": t.concluida}
            for t in itens
        ],
    }
@app.put("/tarefas/concluir")
def put_tarefa(tarefa:TarefaConcluida,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autentica)):
    nome = tarefa.nome.strip()
    if not nome:
        raise HTTPException(status_code=400, detail="nome é obrigatório!")

    db_tarefa=db.query(TarefaDB).filter(TarefaDB.nome==nome).first()
    if not db_tarefa:
        raise HTTPException(status_code=404,detail="tarefa não encontrada!")
    db_tarefa.concluida=True
    db.commit()
    db.refresh(db_tarefa)
    return{"message":"tarefa atualizado com sucesso"}

@app.delete("/tarefas/deletar")
def delete_tarefa(tarefa:TarefaConcluida,db:Session=Depends(sessao_db),credentials:HTTPBasicCredentials=Depends(autentica)):
    nome = tarefa.nome.strip()
    if not nome:
        raise HTTPException(status_code=400, detail="nome é obrigatório!")
    
    db_tarefa=db.query(TarefaDB).filter(TarefaDB.nome==nome).first()
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="tarefa não encontrada!")
    db.delete(db_tarefa)
    db.commit()
    return {"message":"seu tarefa foi deletado."}