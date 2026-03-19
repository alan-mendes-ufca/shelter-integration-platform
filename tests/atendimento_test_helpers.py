import random

from app.models.abrigo import AbrigoModel
from app.models.pessoa import PessoaModel
from app.models.pessoa_rua import PessoaRuaModel
from app.models.profissional import ProfissionalModel


def criar_ids_validos_atendimento() -> tuple[int, int, int]:
    suffix = random.randint(1000, 999999)

    pessoa_sistema = PessoaModel.criar(
        {
            "nome": f"Profissional Teste {suffix}",
            "senha": "senha123",
        }
    )

    profissional = ProfissionalModel.criar(
        {
            "id_pessoa": pessoa_sistema["id_pessoa"],
            "cargo": "assistente_social",
            "registro_conselho": f"CRESS-{suffix}",
        }
    )

    pessoa_rua = PessoaRuaModel.criar(
        {
            "apelido": f"Pessoa Teste {suffix}",
            "descricao_fisica": "Pessoa em situação de rua para testes",
        }
    )

    abrigo = AbrigoModel.criar(
        {
            "nome": f"Abrigo Teste {suffix}",
            "endereco": f"Rua Teste {suffix}",
            "capacidade_total": 50,
            "telefone": None,
        }
    )

    return (
        pessoa_rua["id_pessoa_rua"],
        profissional["id_profissional"],
        abrigo["id_abrigo"],
    )
