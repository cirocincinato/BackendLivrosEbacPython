from typing import Optional
from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials 
#importação do Modelo com Pydantic
from pydantic import BaseModel
import secrets
import os


app=FastAPI()

class Livros(BaseModel):
    nome:str
    autor:str
    ano:int


class LivrosUpdate(BaseModel):
    nome: Optional[str] = None
    autor: Optional[str] = None
    ano: Optional[int] = None

meu_livroszinho={}

EU="a"
SENHA="a"

security=HTTPBasic()

def autenticar_usuario(credentials:HTTPBasicCredentials=Depends(security)):
    usuario_correto=secrets.compare_digest(credentials.username,EU)
    senha_correta=secrets.compare_digest(credentials.password,SENHA)

    if not(usuario_correto and senha_correta):
        raise HTTPException(status_code=401,detail="usuario ou senha incoretos",headers={"WWW-Authenticate":"basic"})
@app.get("/livros")
def get_livros(page:int=1,limit:int=1,credentials:HTTPBasicCredentials=Depends(autenticar_usuario)):
    if page<1 or limit<1:
        raise HTTPException(status_code=400,detail="page ou limit com valor invalido!")
    star=(page-1)*limit
    end=star+limit
    ordem=True
    livros_paginados=sorted(meu_livroszinho.item(),key=lambda x:x[0],ordem=ordem)

    livros_paginados=[
        {"id":id_livro, "nome_livro":livro_data["nome_livro"],"autor_livro":livro_data["autor_livro"],"ano_livro":livro_data["ano_livro"]}
        for id_livro,livro_data in list(meu_livroszinho.items())[star:end]
    ]
    return {
        "page":page,
        "limt":limit,
        "total":len(meu_livroszinho),
        "livros":livros_paginados
    }
@app.post("/adiciona")
def post_livros(idx:int,livros:Livros,redentials:HTTPBasicCredentials=Depends(autenticar_usuario)):
    if idx in meu_livroszinho:
        raise HTTPException(status_code=409,detail="esse livro existe!")
    else:
        meu_livroszinho[idx]=livros.dict()
        return{"message":"livro adicioando com sucesso!"}
    
@app.patch("/atualiza/{idx}")
def patch_livros(idx: int, livros: LivrosUpdate,redentials:HTTPBasicCredentials=Depends(autenticar_usuario)):
    registro = meu_livroszinho.get(idx)
    if registro is None:
        raise HTTPException(status_code=404, detail="esse livro não existe")
    if livros.nome is not None:
        meu_livroszinho["nome"] = livros.nome
    if livros.autor is not None:
        meu_livroszinho["autor"] = livros.autor
    if livros.ano is not None:
        meu_livroszinho["ano"] = livros.ano

    return {"message": "atualizado com sucesso"}
@app.delete("/deletar/{idx}")
def delete_livro(idx:int,redentials:HTTPBasicCredentials=Depends(autenticar_usuario)):
    if idx not in meu_livroszinho:
        raise HTTPException(status_code=404, detail="esse livro nao foi encontrado")
    else:
        del meu_livroszinho[idx]
        return{"message":"livro deletado com sucesso"}