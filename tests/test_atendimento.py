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
