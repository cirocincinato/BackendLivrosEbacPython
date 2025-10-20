from fastapi import FastAPI,HTTPException

app = FastAPI()

tarefas=[]
# read:buscar os dados de tarefas(pois os dados fastapi dev main.py
#estão  contidos dentro da variavel tarefas do tipo array 
#que vai conter a sequencia com vetores ocupando uma valor na posição de memoria
# Que podem ser de firentes tipos "",'':str. 1,0.1:int,float. True,False:boolen)
#fazer converção de dados para facilitar o uso deles dentro de cada metodo do CRUDE
@app.get("/tarefas")
def get_tarefas():
    if not tarefas:
        return {"message":"Não existe nenhum livro!"}
    else:
        return {"livros": tarefas}
#como seria o nome de uma pagina de lista de tarefas...
#imagine o contexto espesifico do armazenamento desses dados do BD;bancode dado ;  
@app.post("/adiciona")
def post(nome_nova_tarefa:str,descricao_nova_tarefa:str):
    for linha in tarefas:
        if linha["nome"]==nome_nova_tarefa:
            raise HTTPException(status_code=400,detail="essa tarefa já existe!")
    tarefas.append({"nome":nome_nova_tarefa,"descrição":descricao_nova_tarefa,"concluída":False})
    return{"massage":"As informações da sua tarefa foram adicionadas com sucesso!"}
@app.put("/atualiza/{nome_tarefa}")
def put(nome_tarefa:str):
    for linha in tarefas:
        if linha["nome"]==nome_tarefa:
            linha["concluída"]=True
            return{"massage":"As informação de tarefa conluida foi atualizada com sucesso!"}
    raise HTTPException(status_code=400,detail="Não existe essa tarefa!")
@app.delete("/deleta/{nome_tarefa}")
def deleta_tarefa(nome_tarefa:str):
    for linha in tarefas:
        if linha["nome"]==nome_tarefa:
            tarefas.remove(linha)
            return{"massage":"As informação de tarefa foi removida com sucesso!"}
    raise HTTPException(status_code=404,detail="Essa tarefa não foi encontrada!")

#api é um tipo de beck-end 
#clientes()--> API --> seus metodos para lidar(validar/invalidar uma informação)