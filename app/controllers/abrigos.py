"""
Controller: Abrigo + Vaga
==========================

Gerencia o fluxo de acolhimento em tempo real.

REGRA DE NEGÓCIO:
- Entrada num abrigo NÃO requer prontuário, mas requer pessoa cadastrada.
- Consentimento NÃO é verificado aqui. Jamais.

DÉBITO TÉCNICO:
- As operações de entrada/saída deveriam ser atômicas (transação).
  Hoje são duas queries em sequência. Implementar suporte a transações
  no Database.query() para resolver isso.
- DELETE /abrigos/:id (desativar) ainda não implementado.
"""

from flask import Blueprint, request, jsonify
from app.models.abrigo import AbrigoModel, VagaModel

# ─── Blueprint: Abrigo ────────────────────────────────────────────────────────
abrigos_bp = Blueprint("abrigos", __name__, url_prefix="/abrigos")


@abrigos_bp.route("", methods=["POST"])
def criar_abrigo():
    """
    POST /abrigos

    Cadastra um novo abrigo com capacidade total e endereço.

    Body JSON:
        nome             (str, obrigatório)
        endereco         (str, obrigatório)
        capacidade_total (int, obrigatório, > 0)
        telefone         (str, opcional)

    Retorna:
        201 + abrigo criado
        400 se campos obrigatórios faltarem ou capacidade_total inválida
    """
    abrigo = AbrigoModel.criar(request.get_json(silent=True))

    if not abrigo:
        return jsonify({"erro": "Falha ao criar abrigo."}), 500

    return jsonify(abrigo), 201


@abrigos_bp.route("", methods=["GET"])
def listar_abrigos():
    """
    GET /abrigos
    GET /abrigos?vagas=disponivel

    Lista todos os abrigos ativos.
    Com ?vagas=disponivel, filtra apenas os que têm vagas livres (US07).

    Retorna:
        200 + lista de abrigos
    """
    apenas_com_vagas = request.args.get("vagas") == "disponivel"

    try:
        abrigos = AbrigoModel.listar(apenas_com_vagas=apenas_com_vagas)
    except Exception as err:
        return (
            jsonify({"erro": "Erro interno ao listar abrigos.", "detalhes": str(err)}),
            500,
        )

    return jsonify(abrigos), 200


# ─── Blueprint: Vaga ──────────────────────────────────────────────────────────
vagas_bp = Blueprint("vagas", __name__, url_prefix="/vagas")


@vagas_bp.route("/entrada", methods=["POST"])
def registrar_entrada():
    """
    POST /vagas/entrada

    Registra a entrada de uma pessoa em um abrigo (US08).
    Cria o registro de ocupação e decrementa o contador de vagas.

    Body JSON:
        pessoa_id (int, obrigatório)
        abrigo_id (int, obrigatório)

    Retorna:
        201 + registro da vaga
        400 se campos faltarem
        409 se não houver vagas disponíveis ou pessoa já estiver acolhida
    """
    dados = request.get_json(silent=True) or {}
    vaga = VagaModel.registrar_entrada(dados.get("pessoa_id"), dados.get("abrigo_id"))

    return jsonify(vaga), 201


@vagas_bp.route("/<int:vaga_id>/saida", methods=["PUT"])
def registrar_saida(vaga_id: int):
    """
    PUT /vagas/:id/saida

    Registra a saída de uma pessoa do abrigo (US09).
    Libera a vaga e incrementa o contador do abrigo.

    Parâmetro de rota:
        vaga_id (int): ID do registro de ocupação.

    Retorna:
        200 + vaga atualizada (status='liberada')
        404 se a vaga não existir
        409 se a saída já tiver sido registrada
    """
    vaga = VagaModel.registrar_saida(vaga_id)

    return jsonify(vaga), 200
