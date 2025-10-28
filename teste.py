from typing import Optional
from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials 
#importação do Modelo com Pydantic
from pydantic import BaseModel
import secrets
import os

app=FastAPI(
    title="projeto de tarefas sendo feito novamente",
    description="primeira vercao basica"
)
class Tarefa(BaseModel):
    nome:str
    descricao:str
    concluida:bool=False
class TarefaConcluida(BaseModel):
    nome:str
tarefas:list[Tarefa] = []
@app.post("/tarefas/adicionar", status_code=201)
def post_tarefa(tarefa:Tarefa):
    if not tarefa.nome:
        raise HTTPException(400, "nome é obrigatório")
    if not tarefa.descricao:
        raise HTTPException(400, "descrição é obrigatório")
    existe=any(tarefa.nome.strip().casefold()==linha.nome.strip().casefold() for linha in tarefas)
    if existe:
        raise HTTPException(status_code=409, detail="essa tarefa nao pode ser adicionada!")
    else:
        nova_tarefa=tarefa
        tarefas.append(nova_tarefa)
        return tarefa
@app.get("/tarefas/mostrar", status_code=200)
def get_tarefas():
    return{"tarefas":tarefas}

@app.put("/tarefas/concluir")
def put_tarefa(tarefa:TarefaConcluida):
    if not tarefa.nome:
        raise HTTPException(400, "nome é obrigatório")
    existe=any(tarefa.nome.strip().casefold()==linha.nome.strip().casefold() for linha in tarefas)
    if existe:
        for linha in tarefas:
            if tarefa.nome.strip().casefold()==linha.nome.strip().casefold():
                linha.concluida=True
                return {"message":"tarefa atualizada"}
    raise HTTPException(status_code=404, detail="tarefa não encontrada")
@app.delete("/tarefas/deletar")
def delete_tarefa(tarefa:TarefaConcluida):
    if not tarefa.nome:
        raise HTTPException(400, "nome é obrigatório")
    existe=any(tarefa.nome.strip().casefold()==linha.nome.strip().casefold() for linha in tarefas)
    if existe:
        for i,t in enumerate(tarefas):
            if tarefa.nome.strip().casefold()==t.nome.strip().casefold():
                tarefas.pop(i)
                return {"message": "tarefa removida com sucesso"}
    raise HTTPException(status_code=404, detail="tarefa não encontrada")