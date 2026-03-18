import random
from datetime import datetime

import requests

from app.models.atendimento import AtendimentoModel
from tests.atendimento_test_helpers import criar_ids_validos_atendimento


def test_with_invalid_id():
    invalid_id = random.randint(100000, 999999)
    response = requests.get(f"http://127.0.0.1:5000/api/v1/atendimentos/{invalid_id}")

    assert response.status_code == 404

    responseBody = response.json()
    assert responseBody == {
        "name": "NotFoundError",
        "message": "Usuário não encontrado.",
        "action": "Contate o suporte.",
        "status_code": 404,
    }


def test_with_valid_pessoa_id():
    pessoa_id, profissional_id = criar_ids_validos_atendimento()

    created_atendimento = AtendimentoModel.registrar(
        {
            "id_pessoa_rua": pessoa_id,
            "id_profissional": profissional_id,
            "tipo": "escuta",
            "unidade": "Unidade Centro",
            "observacoes": "Teste de listagem por pessoa",
        }
    )

    response = requests.get(f"http://127.0.0.1:5000/api/v1/atendimentos/{pessoa_id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1
    assert any(
        item["id_atendimento"] == created_atendimento["id_atendimento"]
        and item["id_pessoa_rua"] == pessoa_id
        for item in body
    )


def test_with_missing_filter_params():
    response = requests.get("http://127.0.0.1:5000/api/v1/atendimentos", params={})

    assert response.status_code == 400
    assert response.json() == {
        "name": "ValidationError",
        "message": "Parâmetros obrigatórios ausentes para filtragem.",
        "action": "Envie 'unidade', 'data_inicio' e 'data_fim' na query string.",
        "status_code": 400,
    }


def test_with_filter_after_register():
    pessoa_id, profissional_id = criar_ids_validos_atendimento()
    unidade_teste = f"Unidade Filtro {random.randint(1000, 9999)}"

    created_atendimento = AtendimentoModel.registrar(
        {
            "id_pessoa_rua": pessoa_id,
            "id_profissional": profissional_id,
            "tipo": "escuta",
            "unidade": unidade_teste,
            "observacoes": "Teste de filtro após registro",
        }
    )

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    response = requests.get(
        "http://127.0.0.1:5000/api/v1/atendimentos",
        params={
            "unidade": unidade_teste,
            "data_inicio": data_hoje,
            "data_fim": data_hoje,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert any(
        item["id_atendimento"] == created_atendimento["id_atendimento"]
        and item["unidade"] == unidade_teste
        for item in body
    )
