from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_calcular_soma(mocker):
    mock_somar_delay=mocker.patch("tasks.somar.delay")
    mock_redi_lpush=mocker.patch("main.redis_client.lpush")
    mock_redis_ltrim=mocker.patch("main.redis_client.ltrim")

    mock_somar_delay.return_value.id="fake-task-id"

    response = client.post("calcular/soma",params={"a":1,"b":2})

    assert response.status_code==200
    assert response.json()=={"task_id":"fake-task-id",
        "message":"Tarefa de soma envida"
        }

def test_calcular_fatorial(mocker):
    mock_fatorial_delay=mocker.patch("tasks.fatorial.delay")
    mock_redi_lpush=mocker.patch("main.redis_client.lpush")
    mock_redis_ltrim=mocker.patch("main.redis_client.ltrim")

    mock_fatorial_delay.return_value.id="fake-task-id"

    response = client.post("calcular/fatorial",params={"n":5})

    assert response.status_code==200
    assert response.json()=={"task_id":"fake-task-id",
        "message":"Tarefa de fatorial envida"
        } 