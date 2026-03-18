"""
Controller: Vaga
================

Endpoints de entrada e saída de pessoas em abrigos.

REGRA DE NEGÓCIO IMPORTANTE:
    Entrada num abrigo NÃO requer prontuário nem consentimento.
    Requer apenas que a pessoa esteja cadastrada (US08, US09).
    Não coloque verificação de consentimento aqui. Jamais.

Débito técnico registrado:
    Entrada/saída deveria ser uma transação atômica no banco.
    Por enquanto, a verificação de disponibilidade ocorre via SELECT
    antes do UPDATE dentro do VagaModel.
"""

from flask import Blueprint, request, jsonify
from app.models.vaga import VagaModel
from infra.erros import ValidationError

vagas_bp = Blueprint("vagas", __name__, url_prefix="/vagas")


@vagas_bp.route("/entrada", methods=["POST"])
def registrar_entrada():
    """
    POST /vagas/entrada

    Registra a entrada de uma pessoa em um abrigo (US08).
    Decrementa vagas_disponiveis do abrigo automaticamente.

    Body JSON esperado:
        {
            "pessoa_id": 42,  (obrigatório)
            "abrigo_id": 3    (obrigatório)
        }

    Retorna:
        201 Created  + registro da vaga criada
        400 Bad Request se campos obrigatórios faltarem
        409 Conflict  se pessoa já estiver acolhida em outro abrigo
        409 Conflict  se o abrigo não tiver vagas disponíveis
    """
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    faltando = {"pessoa_id", "abrigo_id"} - set(dados.keys())
    if faltando:
        raise ValidationError(
            message=f"Campos obrigatórios ausentes: {sorted(faltando)}.",
            action="Envie 'pessoa_id' e 'abrigo_id' no body.",
        )

    try:
        vaga = VagaModel.registrar_entrada(
            pessoa_id=int(dados["pessoa_id"]),
            abrigo_id=int(dados["abrigo_id"]),
        )
    except ValueError as err:
        # ValueError do model = regra de negócio violada
        return jsonify({"erro": str(err)}), 409
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not vaga:
        return jsonify({"erro": "Erro ao registrar entrada."}), 500

    return jsonify(vaga), 201


@vagas_bp.route("/<int:vaga_id>/saida", methods=["PUT"])
def registrar_saida(vaga_id: int):
    """
    PUT /vagas/:id/saida

    Registra a saída da pessoa do abrigo (US09).
    Incrementa vagas_disponiveis do abrigo automaticamente.

    Parâmetro de rota:
        vaga_id (int): ID do registro de ocupação (tabela vaga).

    Retorna:
        200 OK   + vaga atualizada (status='liberada', saida_em preenchido)
        404 Not Found se a vaga não existir
        409 Conflict  se a vaga já estiver liberada
    """
    # Busca antes para distinguir 404 (não existe) de 409 (já liberada)
    try:
        vaga_atual = VagaModel.buscar_por_id(vaga_id)
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not vaga_atual:
        return jsonify({"erro": "Vaga não encontrada."}), 404

    if vaga_atual["status"] == "liberada":
        return jsonify({"erro": "Saída já registrada para esta vaga."}), 409

    try:
        vaga = VagaModel.registrar_saida(vaga_id)
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not vaga:
        return jsonify({"erro": "Erro ao registrar saída."}), 500

    return jsonify(vaga), 200


@vagas_bp.route("/abrigo/<int:abrigo_id>", methods=["GET"])
def listar_vagas_por_abrigo(abrigo_id: int):
    """
    GET /vagas/abrigo/:id

    Lista todas as ocupações de um abrigo (ativas e históricas).
    Inclui o apelido da pessoa via JOIN.

    Parâmetro de rota:
        abrigo_id (int): ID do abrigo.

    Retorna:
        200 OK + lista de vagas (pode ser vazia)
    """
    try:
        vagas = VagaModel.listar_por_abrigo(abrigo_id)
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    return jsonify(vagas), 200


@vagas_bp.route("/pessoa/<int:pessoa_id>", methods=["GET"])
def listar_vagas_por_pessoa(pessoa_id: int):
    """
    GET /vagas/pessoa/:id

    Lista o histórico de abrigos de uma pessoa.
    Inclui nome e endereço do abrigo via JOIN.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa.

    Retorna:
        200 OK + lista de vagas (pode ser vazia)
    """
    try:
        vagas = VagaModel.listar_por_pessoa(pessoa_id)
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    return jsonify(vagas), 200
