"""
Put to api/v1/atendimentos/{id}
"""

import random
import requests

from app.models.atendimento import AtendimentoModel
from tests.atendimento_test_helpers import criar_ids_validos_atendimento


def test_put_with_empty_body():
    response = requests.put("http://127.0.0.1:5000/api/v1/atendimentos/1", json={})

    assert response.status_code == 400
    assert response.json() == {
        "name": "ValidationError",
        "message": "Body JSON inválido ou ausente.",
        "action": "Envie ao menos um campo para atualização.",
        "status_code": 400,
    }


def test_put_with_nonexistent_id():
    nonexistent_id = random.randint(100000, 999999)
    response = requests.put(
        f"http://127.0.0.1:5000/api/v1/atendimentos/{nonexistent_id}",
        json={"tipo": "banho"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "name": "NotFoundError",
        "message": "Atendimento não encontrado.",
        "action": "Verifique o ID informado.",
        "status_code": 404,
    }


def test_put_with_valid_data_updates_record():
    pessoa_id, profissional_id = criar_ids_validos_atendimento()
    created = AtendimentoModel.registrar(
        {
            "id_pessoa_rua": pessoa_id,
            "id_profissional": profissional_id,
            "tipo": "escuta",
            "unidade": "Unidade Inicial",
            "observacoes": "Observacao inicial",
        }
    )

    payload = {
        "tipo": "banho",
        "unidade": "Unidade Atualizada",
        "observacoes": "Observacao atualizada",
    }

    response = requests.put(
        f"http://127.0.0.1:5000/api/v1/atendimentos/{created['id_atendimento']}",
        json=payload,
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["id_atendimento"] == created["id_atendimento"]
    assert updated["tipo"] == payload["tipo"]
    assert updated["unidade"] == payload["unidade"]
    assert updated["observacoes"] == payload["observacoes"]

    response_get = requests.get(
        f"http://127.0.0.1:5000/api/v1/atendimentos/{pessoa_id}"
    )
    assert response_get.status_code == 200
    atendimentos = response_get.json()
    assert any(
        item["id_atendimento"] == created["id_atendimento"]
        and item["tipo"] == payload["tipo"]
        and item["unidade"] == payload["unidade"]
        and item["observacoes"] == payload["observacoes"]
        for item in atendimentos
    )
