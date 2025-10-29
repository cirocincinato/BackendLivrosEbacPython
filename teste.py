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
EU="a"
SENHA="a"
security=HTTPBasic()
def autentica(credentials:HTTPBasicCredentials=Depends(security)):
    usuario_correto=secrets.compare_digest(credentials.username,EU)
    senha_correta=secrets.compare_digest(credentials.password,SENHA)
    if not(usuario_correto and senha_correta):
        raise HTTPException(status_code=401,detail="usuario ou senha incoretos",headers={"WWW-Authenticate":"Basic"})
@app.post("/tarefas/adicionar", status_code=201)
def post_tarefa(tarefa:Tarefa,credentials:HTTPBasicCredentials=Depends(autentica)):
    if not tarefa.nome:
        raise HTTPException(status_code=400,detail="nome é obrigatório")
    if not tarefa.descricao:
        raise HTTPException(status_code=400,detail="descrição é obrigatório")
    existe=any(tarefa.nome.strip().casefold()==linha.nome.strip().casefold() for linha in tarefas)
    if existe:
        raise HTTPException(status_code=409, detail="essa tarefa nao pode ser adicionada!")
    else:
        nova_tarefa=tarefa
        tarefas.append(nova_tarefa)
        return tarefa
    
@app.get("/tarefas/mostrar", status_code=200)
def get_tarefas(page:int=1, limiti:int=1,order:str="asc",order_por:str="nome",credentials:HTTPBasicCredentials=Depends(autentica)):
    if page<1 or limiti<1:
        raise HTTPException(status_code=400, detail="paga ou limit invalidos")
    start=(page-1)*limiti
    end=start+limiti

    order=order.lower()
    if order not in("asc","desc"):
        raise HTTPException(status_code=400,detail="deve ser asc ou desc")
    order=(order=="desc")
    itens=list(enumerate(tarefas))
    order_por=order_por.lower()
    if order_por=="nome":
        ordenado_itens_tarefas=sorted(itens,key=lambda item:item[1].nome.casefold(),reverse =order)
    elif order_por=="descricao":
        ordenado_itens_tarefas=sorted(itens,key=lambda item:item[1].descricao.casefold(),reverse =order)
    elif order_por=="concluida":
        ordenado_itens_tarefas=sorted(itens,key=lambda item:item[1].concluida,reverse =order)
    else:
        raise HTTPException(status_code=400, detail="order_by deve ser 'nome', 'descricao' ou 'concluida'")
    pagina=[
        linha
        for idx,linha in ordenado_itens_tarefas[start:end]
    ]
    return {
        "page": page,
        "limit": limiti,
        "total": len(tarefas),
        "tarefas": pagina
    }

@app.put("/tarefas/concluir")
def put_tarefa(tarefa:TarefaConcluida,credentials:HTTPBasicCredentials=Depends(autentica)):
    if not tarefa.nome:
        raise HTTPException(status_code=400, detail="nome é obrigatório")
    existe=any(tarefa.nome.strip().casefold()==linha.nome.strip().casefold() for linha in tarefas)
    if existe:
        for linha in tarefas:
            if tarefa.nome.strip().casefold()==linha.nome.strip().casefold():
                linha.concluida=True
                return {"message":"tarefa atualizada"}
    raise HTTPException(status_code=404, detail="tarefa não encontrada")
@app.delete("/tarefas/deletar")
def delete_tarefa(tarefa:TarefaConcluida,credentials:HTTPBasicCredentials=Depends(autentica)):
    if not tarefa.nome:
        raise HTTPException(status_code=400, detail="nome é obrigatório")
    existe=any(tarefa.nome.strip().casefold()==linha.nome.strip().casefold() for linha in tarefas)
    if existe:
        for i,t in enumerate(tarefas):
            if tarefa.nome.strip().casefold()==t.nome.strip().casefold():
                tarefas.pop(i)
                return {"message": "tarefa removida com sucesso"}
    raise HTTPException(status_code=404, detail="tarefa não encontrada")