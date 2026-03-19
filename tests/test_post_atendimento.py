"""
Post to api/v1/atendimento
"""

import requests

from tests.atendimento_test_helpers import criar_ids_validos_atendimento


def test_with_empty_data():
    response = requests.post("http://127.0.0.1:5000/api/v1/atendimentos", json={})

    assert response.status_code == 400
    assert response.json() == {
        "name": "ValidationError",
        "message": "Campos obrigatórios faltando ou extras presentes.",
        "action": "Verifique se 'id_pessoa_rua', 'id_profissional', 'id_abrigo' e 'tipo' estão presentes e sem campos adicionais.",
        "status_code": 400,
    }


def test_with_invalid_service_type():
    pessoa_id, profissional_id, abrigo_id = criar_ids_validos_atendimento()

    data_service = {
        "id_pessoa_rua": pessoa_id,
        "id_profissional": profissional_id,
        "id_abrigo": abrigo_id,
        "tipo": "invalid_type",
        "observacoes": "Pessoa relatou...",
    }

    response = requests.post(
        "http://127.0.0.1:5000/api/v1/atendimentos",
        json=data_service,
    )

    assert response.json() == {
        "name": "ValidationError",
        "message": "Campo de 'tipo' preenchido com opção inválida.",
        "action": "Utilize somente uma das opção a seguir: 'escuta', 'alimentacao', 'banho', 'saude', 'juridico', 'outro'.",
        "status_code": 400,
    }


def test_with_valid_data():
    pessoa_id, profissional_id, abrigo_id = criar_ids_validos_atendimento()

    data_service = {
        "id_pessoa_rua": pessoa_id,
        "id_profissional": profissional_id,
        "id_abrigo": abrigo_id,
        "tipo": "escuta",
        "observacoes": "Pessoa relatou...",
    }

    response = requests.post(
        "http://127.0.0.1:5000/api/v1/atendimentos",
        json=data_service,
    )

    assert response.status_code == 201
    created = response.json()
    print(created)
    assert set(data_service).issubset(set(created))
    assert "id_atendimento" in created

    response_get = requests.get(
        f"http://127.0.0.1:5000/api/v1/atendimentos/{pessoa_id}"
    )
    assert response_get.status_code == 200
    atendimentos = response_get.json()
    assert any(
        item["id_atendimento"] == created["id_atendimento"] for item in atendimentos
    )
