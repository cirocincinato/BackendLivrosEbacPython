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
    nome_tarefa:str
    descricao_tarefa:str
    concluida:bool = False
#para poder mandar um corpo apenas com nome
class TarefaExistente(BaseModel):
    nome_tarefa:str

tarefas: list[Tarefa] = []

@app.get("/tarefas")
def get_tarefas():
    if not tarefas:
        return {"message":"Não existe nenhuma tarefa!"}
    else:
        return tarefas
#como seria o nome de uma pagina de lista de tarefas...
#imagine o contexto espesifico do armazenamento desses dados do BD;bancode dado ;  
#Na rota de adicionar tarefa (POST), em vez de receber um dicionário, receba um objeto do tipo Tarefa como parâmetro.
@app.post("/adiciona")
def post_tarefa(tarefa:Tarefa):
    for linha in tarefas:
        if linha.nome_tarefa==tarefa.nome_tarefa:
            raise HTTPException(status_code=400,detail="essa tarefa já existe!")
    tarefas.append(tarefa)
    return{"massage":"As informações da sua tarefa foram adicionadas com sucesso!"}
@app.put("/atualiza")
def put_tarefa(tarefa:TarefaExistente):
    for linha in tarefas:
        if linha.nome_tarefa==tarefa.nome_tarefa:
            linha.concluida=True
            return{"massage":"As informação de tarefa conluida foi atualizada com sucesso!"}
    raise HTTPException(status_code=400,detail="Não existe essa tarefa!")
@app.delete("/deleta")
def deleta_tarefa(tarefa:TarefaExistente):
    for linha in tarefas:
        if linha.nome_tarefa==tarefa.nome_tarefa:
            tarefas.remove(linha)   
            return{"massage":"As informação de tarefa foi removida com sucesso!"}
    raise HTTPException(status_code=404,detail="Essa tarefa não foi encontrada!")

#api é um tipo de beck-end 
#clientes()--> API --> seus metodos para lidar(validar/invalidar uma informação)