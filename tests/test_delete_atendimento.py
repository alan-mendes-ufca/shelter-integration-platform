"""
Delete to api/v1/atendimentos/{id}
"""

import random
import requests

from app.models.atendimento import AtendimentoModel
from tests.atendimento_test_helpers import criar_ids_validos_atendimento


def _create_person_and_atendimento() -> int:
    pessoa_id, profissional_id = criar_ids_validos_atendimento()

    atendimento = AtendimentoModel.registrar(
        {
            "id_pessoa_rua": pessoa_id,
            "id_profissional": profissional_id,
            "tipo": "escuta",
            "unidade": "Unidade Delete",
        }
    )

    return atendimento["id_atendimento"], pessoa_id


def test_delete_with_nonexistent_id():
    nonexistent_id = random.randint(100000, 999999)
    response = requests.delete(
        f"http://127.0.0.1:5000/api/v1/atendimentos/{nonexistent_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "name": "NotFoundError",
        "message": "Atendimento não encontrado.",
        "action": "Verifique o ID informado.",
        "status_code": 404,
    }


def test_delete_with_valid_id():
    atendimento_id, pessoa_id = _create_person_and_atendimento()

    response = requests.delete(
        f"http://127.0.0.1:5000/api/v1/atendimentos/{atendimento_id}"
    )

    assert response.status_code == 204
    assert response.text == ""

    response_get = requests.get(
        f"http://127.0.0.1:5000/api/v1/atendimentos/{pessoa_id}"
    )
    assert response_get.status_code == 200
    atendimentos = response_get.json()
    assert all(item["id_atendimento"] != atendimento_id for item in atendimentos)
