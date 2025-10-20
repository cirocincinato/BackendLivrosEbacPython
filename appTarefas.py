from fastapi import FastAPI,HTTPException
#importação do Modelo com Pydantic
from pydantic import BaseModel
app = FastAPI()


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

@app.get("/tarefas")
def get_tarefas():
    if not tarefas:
        return {"message":"Não existe nenhuma tarefa!"}
    else:
        return tarefas
#como seria o nome de uma pagina de lista de tarefas...
#imagine o contexto espesifico do armazenamento desses dados do BD;bancode dado ;  
#Na rota de adicionar tarefa (POST), em vez de receber um dicionário, receba um objeto do tipo Tarefa como parâmetro.

#como seria o nome de uma pagina de lista de tarefas...
#imagine o contexto espesifico do armazenamento desses dados do BD;bancode dado ;  
#Agora recebe um objeto JSON no corpo da requisição, e o FastAPI converte para o tipo Tarefa.
@app.post("/adiciona")
def post(tarefa:Tarefa):
    for linha in tarefas:
        if linha.nome==tarefa.nome:
            raise HTTPException(status_code=400,detail="essa tarefa já existe!")
    tarefas.append(tarefa)
    return {"message": "Tarefa adicionada com sucesso!"}
@app.put("/atualiza")
def put(tarefaExis:TarefaExistente):
    for linha in tarefas:
        if linha.nome==tarefaExis.nome:
            linha.concluida=True
            return{"message":"As informação de tarefa conluida foi atualizada com sucesso!"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada!")
@app.delete("/deleta")
def deleta_tarefa(tarefaExis:TarefaExistente):
    for linha in tarefas:
        if linha.nome==tarefaExis.nome:
            tarefas.remove(linha)
            return {"message": "Tarefa removida com sucesso!"}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada!")
#api é um tipo de beck-end 
#clientes()--> API --> seus metodos para lidar(validar/invalidar uma informação)