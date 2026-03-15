"""
Post to api/v1/atendimento
"""

import requests


def test_with_empty_data():
    response = requests.post("http://127.0.0.1:5000/api/v1/atendimentos", json={})

    assert response.status_code == 400
    assert response.json() == {
        "name": "ValidationError",
        "message": "Campos obrigatórios faltando ou extras presentes.",
        "action": "Verifique se 'pessoa_id', 'profissional_id', 'tipo' e 'unidade' estão presentes e sem campos adicionais.",
        "status_code": 400,
    }


def test_with_invalid_service_type():
    data_service = {
        "pessoa_id": 42,
        "profissional_id": 7,
        "tipo": "invalid_type",
        "unidade": "CREAS Centro",
        "observacoes": "Pessoa relatou...",
        "realizado_em": "2026-03-05 14:30",
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
    data_service = {
        "pessoa_id": 42,
        "profissional_id": 7,
        "tipo": "escuta",
        "unidade": "CREAS Centro",
        "observacoes": "Pessoa relatou...",
        "realizado_em": "2026-03-05 14:30",
    }

    response = requests.post(
        "http://127.0.0.1:5000/api/v1/atendimentos",
        json=data_service,
    )

    assert response.status_code == 201
    assert set(data_service).issubset(set(response.json()))
