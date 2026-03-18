"""
Controller: Abrigo + Vaga
==========================

Estagiário, esses dois controllers gerenciam o fluxo de acolhimento em tempo real.

O ponto mais delicado é a CONSISTÊNCIA entre as duas operações de entrada/saída:
quando você registra uma entrada (POST /vagas/entrada), duas coisas precisam acontecer:
  1. INSERT em `vaga` com status='ocupada'
  2. UPDATE em `abrigo` decrementando `vagas_disponiveis`

Se uma funcionar e a outra falhar, o sistema fica inconsistente.
Idealmente isso seria uma transação de banco de dados, mas como nosso Database.query()
executa uma query por vez, por enquanto verificamos manualmente a disponibilidade
antes de confirmar a entrada.

Anote como débito técnico: "Implementar suporte a transações no Database.query()".

REGRA DE NEGÓCIO IMPORTANTE:
- Entrada num abrigo NÃO requer prontuário, mas requer pessoa cadastrada.
- Não coloque verificação de consentimento aqui. Jamais.
"""

from flask import Blueprint, request, jsonify  # noqa: F401
from app.models.abrigo import AbrigoModel, VagaModel  # noqa: F401

# ─── Blueprint: Abrigo ────────────────────────────────────────────────────────
abrigos_bp = Blueprint("abrigos", __name__, url_prefix="/abrigos")


@abrigos_bp.route("", methods=["POST"])
def criar_abrigo():
    """
    POST /abrigos

    Cadastra um novo abrigo no sistema com capacidade total e endereço.

    Body JSON esperado:
        {
            "nome": "Abrigo Esperança",         (obrigatório)
            "endereco": "Rua das Flores, 100",  (obrigatório)
            "capacidade_total": 50,             (obrigatório, inteiro positivo)
            "telefone": "(11) 9999-9999"        (opcional)
        }

    Retorna:
        201 Created + dados do abrigo
        400 Bad Request se campos obrigatórios faltarem ou capacidade_total <= 0

    TODO (estagiário): Valide que capacidade_total é um inteiro positivo.
                       No model, `vagas_disponiveis` começa igual a `capacidade_total`.
                       Não permita que o frontend defina vagas_disponiveis diretamente.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@abrigos_bp.route("", methods=["GET"])
def listar_abrigos():
    """
    GET /abrigos
    GET /abrigos?vagas=disponivel

    Lista todos os abrigos ativos. Se o query param `vagas=disponivel` for
    passado, filtra apenas os abrigos com vagas livres (US07).

    Query param (opcional):
        vagas (str): Se "disponivel", filtra abrigos com vagas > 0.

    Retorna:
        200 OK + lista de abrigos (com contagem de vagas disponíveis)

    TODO (estagiário): Use request.args.get('vagas') para capturar o filtro.
                       apenas_com_vagas = request.args.get('vagas') == 'disponivel'
                       Passe isso para AbrigoModel.listar(apenas_com_vagas).
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


# ─── Blueprint: Vaga ──────────────────────────────────────────────────────────
vagas_bp = Blueprint("vagas", __name__, url_prefix="/vagas")


@vagas_bp.route("/entrada", methods=["POST"])
def registrar_entrada():
    """
    POST /vagas/entrada

    Registra a entrada de uma pessoa em um abrigo.
    Altera status para "Ocupada" e decrementa o contador de vagas (US08).

    Body JSON esperado:
        {
            "pessoa_id": 42,   (obrigatório)
            "abrigo_id": 3     (obrigatório)
        }

    Retorna:
        201 Created + registro da vaga
        400 Bad Request se campos faltarem
        409 Conflict se não houver vagas disponíveis no abrigo
        409 Conflict se a pessoa já estiver acolhida em outro abrigo

    TODO (estagiário): O VagaModel.registrar_entrada() já faz as verificações internas,
                       mas é boa prática também capturar exceções aqui e retornar
                       mensagens amigáveis. Não deixe stack traces vazarem para o cliente.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@vagas_bp.route("/<int:vaga_id>/saida", methods=["PUT"])
def registrar_saida(vaga_id: int):
    """
    PUT /vagas/:id/saida

    Registra a saída da pessoa do abrigo.
    Libera a vaga e incrementa o contador de vagas do abrigo (US09).

    Parâmetro de rota:
        vaga_id (int): ID do registro de ocupação (tabela `vaga`).

    Retorna:
        200 OK + vaga atualizada (status='liberada', saida_em preenchido)
        404 Not Found se a vaga não existir
        409 Conflict se a vaga já estiver liberada (saída já registrada)

    TODO (estagiário): Chame VagaModel.registrar_saida(vaga_id).
                       Se retornar None, a vaga não existe ou já estava liberada.
                       Tente diferenciar os dois casos consultando a vaga antes.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501
