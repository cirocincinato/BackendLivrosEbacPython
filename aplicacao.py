from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
import secrets
app=FastAPI(
    title="API de Livros",
    description="A aplicação possui um único usuário fixo com email e senha pré-definidos.O endpoint de autenticação verifica se as credenciais fornecidas são corretas.",
    version="1.0.0",
    contact={
        "name":"Ciro Da Rocha",
        "email":"cirocincinato1@gmail.com"
    }
)

MEU_USUARIO="usuario@email.com"
MINHA_SENHA="senha123"
security=HTTPBasic()
def autenticar_meu_usuario(credentials:HTTPBasicCredentials=Depends(security)):
    is_username_correct=secrets.compare_digest(credentials.username,MEU_USUARIO)
    is_password_correct=secrets.compare_digest(credentials.password,MINHA_SENHA)

    if not(is_username_correct and is_password_correct):
        raise HTTPException(status_code=401, detail="usuário ou senha incorretos", headers={"WWW-Authenticate":"Basic"})

@app.get("/autenticacao") 
def get_autenticacao(credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    return "Autenticado com sucesso!"