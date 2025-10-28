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

@app.get("/livros")
def get_livros():
    if not meu_livroszinho:
        return{"livros": []}
    else:
        return{"livros":meu_livroszinho}
@app.post("/adiciona")
def post_livros(idx:int,livros:Livros):
    if idx in meu_livroszinho:
        raise HTTPException(status_code=409,detail="esse livro existe!")
    else:
        meu_livroszinho[idx]=livros.dict()
        return{"message":"livro adicioando com sucesso!"}
    
@app.patch("/atualiza/{idx}")
def patch_livros(idx: int, livros: LivrosUpdate):
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
def delete_livro(idx:int):
    if idx not in meu_livroszinho:
        raise HTTPException(status_code=404, detail="esse livro nao foi encontrado")
    else:
        del meu_livroszinho[idx]
        return{"message":"livro deletado com sucesso"}