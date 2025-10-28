
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



app=FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros.",
    version="1.0.0",
    contact={
        "name":"Ciro Da Rocha",
        "email":"cirocincinato1@gmail.com"
    }
)

MEU_USUARIO="admin"
MINHA_SENHA="admin"

security=HTTPBasic()

meus_livrozinhos={}

#POO:hernça sendo passada. essa clase ajuda a definir o formato das informáções
#assim o proximo passo é ajustar todos os metos para que se 
# adapitem há essa classe:class Livros(BaseModel):
class Livro(BaseModel):
    nome_livro:str
    autor_livro:str
    ano_livro:int

def autenticar_meu_usuario(credentials:HTTPBasicCredentials=Depends(security)):
    is_username_correct=secrets.compare_digest(credentials.username,MEU_USUARIO)
    is_password_correct=secrets.compare_digest(credentials.password,MINHA_SENHA)

    if not(is_username_correct and is_password_correct):
        raise HTTPException(status_code=401, detail="usuário ou senha incorretos", headers={"WWW-Authenticate":"Basic"})

#paginação somente no meto GET
@app.get("/livros")
def get_livros(page: int=1,limit:int=10,credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    if page < 0 or limit<=0:
        raise HTTPException(status_code=400,detail="page ou limit estão com valores inválidos!!")
    if not meus_livrozinhos:
        return {"message":"Não existe nenhum livro!!"}
    
    livros_ordenados=sorted(meus_livrozinhos.items(),key=lambda item:item[0])

    start=(page-1)*limit
    end=start+limit


    livro_paginados=[
        {"id":id_livro, "nome_livro":livro_data["nome_livro"],"autor_livro":livro_data["autor_livro"],"ano_livro":livro_data["ano_livro"]}
        for id_livro,livro_data in livros_ordenados [start:end] 
    ]
    return {
        "page":page,
        "limit":limit,
        "total":len(meus_livrozinhos),
        "livros":livro_paginados
    }
    
# id do livro
# nome do livro
# autor do livro
# ano de lançamento do livro    
@app.post("/adiciona")
def post_livros(id_livro:int,livro:Livro,credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    if id_livro in meus_livrozinhos:
        raise HTTPException(status_code=400,detail="esse livro ja existe!")
    else:
        meus_livrozinhos[id_livro]=livro.dict()
        return{"massage":"As informações do seu livro foram atualizadas com sucesso!"}

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
def put_livro(id_livro:int,livro:Livro,credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    meu_livro=meus_livrozinhos.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code=400,detail="Não existe esse livro!")
    else:
        #eu jogo essa informação dentro do meu antigo dicionário(que é meus_livrozinhos)
        #e não dentro da referencia do antigo dicionário
        # antigo dicionário !=referencia do antigo dicioanrio
        meus_livrozinhos[id_livro]=livro.dict()
        return{"massage":"As informações do seu livro foram atualizadas com sucesso!"}

@app.delete("/deletar/{id_livro}")
def delete_livro(id_livro:int,credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):    
    if id_livro not in meus_livrozinhos:
        raise HTTPException(status_code=404,detail="Esse livro não foi encontrado")
    else:
        del meus_livrozinhos[id_livro]
        return{"message":"seu livro foi deletado"}
