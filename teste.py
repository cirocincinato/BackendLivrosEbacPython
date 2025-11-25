from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

# Modelo de dados Pydantic
class Livro(BaseModel):
    nome: str
    autor: str
    ano: int

# Banco de dados em memória
livros_memoria = []

# Instância principal da API
app = FastAPI(
    title="API de Livros",
    description="API para gerenciar catálogo de livros.",
    version="1.0.1",
    contact={
        "name": "Ciro Da Rocha",
        "email": "cirocincinato1@gmail.com"
    }
)

# GET: Listar todos os livros
@app.get("/livros")
async def get_livros():
    await asyncio.sleep(1)
    return {"livros": livros_memoria}

# POST: Adicionar novo livro
@app.post("/livros")
async def post_livros(id: int, livro: Livro):
    await asyncio.sleep(1)

    # Verificar duplicidade
    if any(item["id_livro"] == id for item in livros_memoria):
        raise HTTPException(status_code=400, detail="Esse livro já existe")

    # Adicionar
    livros_memoria.append({
        "id_livro": id,
        "nome": livro.nome,
        "autor": livro.autor,
        "ano": livro.ano
    })

    return {"mensagem": "Livro adicionado com sucesso"}

# PUT: Atualizar livro existente
@app.put("/livros/{id}")
async def put_livros(id: int, livro: Livro):
    await asyncio.sleep(1)

    for item in livros_memoria:
        if item["id_livro"] == id:
            item["nome"] = livro.nome
            item["autor"] = livro.autor
            item["ano"] = livro.ano

            return {"mensagem": "Livro atualizado com sucesso"}

    raise HTTPException(status_code=404, detail="Livro não encontrado")

# DELETE: Deletar livro
@app.delete("/livros/{id}")
async def delete_livros(id: int):
    await asyncio.sleep(1)

    for item in livros_memoria:
        if item["id_livro"] == id:
            livros_memoria.remove(item)
            return {"mensagem": "Livro deletado com sucesso"}

    raise HTTPException(status_code=404, detail="Livro não encontrado")
