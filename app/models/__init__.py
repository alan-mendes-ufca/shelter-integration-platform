"""
Pacote de Models — Camada de Acesso a Dados
============================================

Estagiário, esse __init__.py serve para facilitar as importações.

Em vez de escrever:
    from app.models.pessoa_rua import PessoaRuaModel

Você pode escrever:
    from app.models import PessoaRuaModel

Sempre que criar um novo model, adicione-o aqui também.
"""

from .pessoa_rua import PessoaRuaModel
from .consentimento import ConsentimentoModel
from .atendimento import AtendimentoModel
from .profissional import ProfissionalModel
from .prontuario import ProntuarioModel
from .abrigo import AbrigoModel, VagaModel
from .encaminhamento import EncaminhamentoModel

__all__ = [
    "PessoaRuaModel",
    "ConsentimentoModel",
    "AtendimentoModel",
    "ProfissionalModel",
    "ProntuarioModel",
    "AbrigoModel",
    "VagaModel",
    "EncaminhamentoModel",
]
