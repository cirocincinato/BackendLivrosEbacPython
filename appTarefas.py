from fastapi import FastAPI,HTTPException,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials 
#importação do Modelo com Pydantic
from pydantic import BaseModel
import secrets
import os
app = FastAPI(title="API de Tarefas",
              description="API que gerencia Tarefas",
              version="0.0.1",
              contact={
                  "name":"Ciro da Rocha",
                  "email":"ciroreipesa@gmail.com"
            }
        )


# read:buscar os dados de tarefas(pois os dados fastapi dev main.py
#estão  contidos dentro da variavel tarefas do tipo array 
#que vai conter a sequencia com vetores ocupando uma valor na posição de memoria
# Que podem ser de firentes tipos "",'':str. 1,0.1:int,float. True,False:boolen)
#fazer converção de dados para facilitar o uso deles dentro de cada metodo do CRUDE

#ciação do Modelo com Pydantic
class Tarefa(BaseModel):
    nome:str
    descricao:str
    concluida:bool=False
class TarefaExistente(BaseModel):
    nome:str
#Isso faz com que cada item da lista seja validado e convertido automaticamente.
tarefas:list[Tarefa]=[]

#crindo aut emticador para usuario

MEU_USUARIO="a" 
MINHA_SENHA="a"

security=HTTPBasic()

def autenticar_meu_usuario(credentials:HTTPBasicCredentials=Depends(security)):
    is_username_correct=secrets.compare_digest(credentials.username,MEU_USUARIO)
    is_password_correct=secrets.compare_digest(credentials.password,MINHA_SENHA)
    if not(is_password_correct and is_username_correct):
        raise HTTPException(status_code=401,detail="usuário ou senha incorretos", headers={"WWW-Authenticate":"Basic"})
    

@app.get("/tarefas")#order_by: str = "id" está ordenando por id, mas da para passa outro parametro pela URL.
def get_tarefas(page:int=1,limit:int=5, order_by: str = "id",  direction: str = "asc",  credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
# direction: str = "asc" premit escilher se vai ser em ordem cresente(`asc`) ou decresente
    if page<1 or limit<1:
        raise HTTPException(status_code=400,detail="page ou limit estão com valores inválidos!!")
    if not tarefas:
        return {"message":"Não existe nenhuma tarefa!!"}
    
    #tarefas_ordenadas=sorted(enumerate(tarefas),key=lambda item:item[0])
    #pares (id, dados)
    itens=list(enumerate(tarefas))

    #ordenação 

    direction=direction.lower()

    if direction not in("asc","desc"):
        raise HTTPException(status_code=400, detail="direction deve ser 'asc' ou 'desc'")

    reverse=(direction=="desc")
    order_by = order_by.lower()
    if order_by=="id":
        itens_ordenados=sorted(itens,key=lambda item:item[0],reverse=reverse)
    elif order_by=="nome":
        itens_ordenados=sorted(itens, key=lambda item:item[1].nome.casefold(),reverse=reverse)
    elif order_by=="descricao":
        itens_ordenados=sorted(itens, key=lambda item:item[1].descricao.casefold(),reverse=reverse)
    elif order_by=="concluida":
         itens_ordenados=sorted(itens,key=lambda item:item[1].concluida,reverse=reverse)
    else:
        raise HTTPException(status_code=400, detail="order_by deve ser 'id', 'nome', 'descricao' ou 'concluida'")
    


    start =(page-1)*limit
    end=start+limit

    tarefas_paginadas=[

        {"id":idx,
         "nome":t.nome,
         "descricao":t.descricao,
         "concluida":t.concluida
        }
        for idx,t in itens_ordenados[start :end]
    ]

    return{
        "page":page,
        "limit":limit,
        "total":len(tarefas),
        "tarefas":tarefas_paginadas
    }

   
    
#como seria o nome de uma pagina de lista de tarefas...
#imagine o contexto espesifico do armazenamento desses dados do BD;bancode dado ;  
#Na rota de adicionar tarefa (POST), em vez de receber um dicionário, receba um objeto do tipo Tarefa como parâmetro.

#como seria o nome de uma pagina de lista de tarefas...
#imagine o contexto espesifico do armazenamento desses dados do BD;bancode dado ;  
#Agora recebe um objeto JSON no corpo da requisição, e o FastAPI converte para o tipo Tarefa.
@app.post("/adiciona")
def post(tarefa:Tarefa,credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    for linha in tarefas:
        if linha.nome==tarefa.nome:
            raise HTTPException(status_code=400,detail="essa tarefa já existe!")
    tarefas.append(tarefa)
    return {"message": "Tarefa adicionada com sucesso!"}
@app.put("/atualiza")
def put(tarefaExis:TarefaExistente,credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    for linha in tarefas:
        if linha.nome==tarefaExis.nome:
            linha.concluida=True
            return{"message":"As informação de tarefa conluida foi atualizada com sucesso!"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada!")
@app.delete("/deleta")
def deleta_tarefa(tarefaExis:TarefaExistente,credentials:HTTPBasicCredentials=Depends(autenticar_meu_usuario)):
    for linha in tarefas:
        if linha.nome==tarefaExis.nome:
            tarefas.remove(linha)
            return {"message": "Tarefa removida com sucesso!"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada!")
#api é um tipo de beck-end 
#clientes()--> API --> seus metodos para lidar(validar/invalidar uma informação)