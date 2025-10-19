
#API de livros

#GET, POST,PUT,DELETE

#POST - Adicionar novos livros(create)
#GET - buscar os dados dos livros(read)
#PUT - Atualizar informações dos livros(update)
#DELETE - Deletar informações dps livros(delete)

#CRUDE é =

#create
#   
#update
#delete

# Vamos acessar nosso ENDPOINT -->http://127.0.0.1:8000
# E vamos acessar os PATH's desse endpoint-->/adiciona
# -->?id_livro=1&nome_livro=ciro rei persa&autor_livro=ciro&ano_livro=2025

#final exemplo usando o POST -->http://127.0.0.1:8000/adiciona?id_livro=1&nome_livro=ciro%20rei%20persa&autor_livro=ciro&ano_livro=2025

from fastapi import FastAPI,HTTPException


app=FastAPI()

meus_livrozinhos={}

@app.get("/livros")
def get_livros():
    if not meus_livrozinhos:
        return {"message":"Não existe nenhum livro!"}
    else:
        return {"livros": meus_livrozinhos}
    
# id do livro
# nome do livro
# autor do livro
# ano de lançamento do livro    
@app.post("/adiciona")
def post_livros(id_livro:int,nome_livro:str,autor_livro:str,ano_livro:int):
    if id_livro in meus_livrozinhos:
        raise HTTPException(status_code=400,detail="esse livro ja existe!")
    else:
        meus_livrozinhos[id_livro]={"nome_livro":nome_livro,"autor_livro":autor_livro, "ano_livro":ano_livro}
        return{"massage":"As informações do seu livro foram atualizadas com sucesso!"}

#precisamos atualizar a informação especificando quem é com id_livro
#1.quem é o livro(id_livro)
#2.pegar o livro(id_livro)
#3.atualização de informações do livro
@app.put("/atualiza/{id_livro}")
def put_livro(id_livro:int,nome_livro:str,autor_livro:str,ano_livro:int):
    meu_livro=meus_livrozinhos.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code=400,detail="Não existe esse livro!")
    else:
        if nome_livro:
            meu_livro["nome_livro"]=nome_livro
        if autor_livro:
            meu_livro["autor_livro"]=autor_livro
        if ano_livro:
            meu_livro["ano_livro"]=ano_livro
        return{"massage":"As informações do seu livro foram atualizadas com sucesso!"}

@app.delete("/deletar/{id_livro}")
def delete_livro(id_livro:int):    
    if id_livro not in meus_livrozinhos:
        raise HTTPException(status_code=404,detail="Esse livro não foi encontrado")
    else:
        del meus_livrozinhos[id_livro]
        return{"message":"seu livro foi deletado"}
