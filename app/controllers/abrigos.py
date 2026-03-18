"""
Controller: Abrigo
==================

Endpoints de cadastro e listagem de abrigos.

Não há verificação de consentimento aqui.
Abrigo é infraestrutura — não dado sensível da pessoa.
"""

from flask import Blueprint, request, jsonify
from app.models.abrigo import AbrigoModel
from infra.erros import ValidationError

abrigos_bp = Blueprint("abrigos", __name__, url_prefix="/abrigos")


@abrigos_bp.route("", methods=["POST"])
def criar_abrigo():
    """
    POST /abrigos

    Cadastra um novo abrigo no sistema.

    Body JSON esperado:
        {
            "nome": "Abrigo Esperança",         (obrigatório)
            "endereco": "Rua das Flores, 100",  (obrigatório)
            "capacidade_total": 50,             (obrigatório, inteiro positivo)
            "telefone": "(85) 9999-9999"        (opcional)
        }

    Retorna:
        201 Created  + dados do abrigo criado
        400 Bad Request se campos obrigatórios faltarem ou forem inválidos
    """
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    faltando = {"nome", "endereco", "capacidade_total"} - set(dados.keys())
    if faltando:
        raise ValidationError(
            message=f"Campos obrigatórios ausentes: {sorted(faltando)}.",
            action="Envie 'nome', 'endereco' e 'capacidade_total' no body.",
        )

    try:
        abrigo = AbrigoModel.criar(dados)
    except ValueError as err:
        return jsonify({"erro": str(err)}), 400
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not abrigo:
        return jsonify({"erro": "Erro ao criar abrigo."}), 500

    return jsonify(abrigo), 201


@abrigos_bp.route("", methods=["GET"])
def listar_abrigos():
    """
    GET /abrigos
    GET /abrigos?vagas=disponivel

    Lista todos os abrigos ativos.
    Com ?vagas=disponivel, filtra apenas os que têm vagas livres (US07).

    Query param (opcional):
        vagas (str): "disponivel" → filtra abrigos com vagas_disponiveis > 0.

    Retorna:
        200 OK + lista de abrigos (pode ser vazia)
    """
    apenas_com_vagas = request.args.get("vagas") == "disponivel"

    try:
        abrigos = AbrigoModel.listar(apenas_com_vagas=apenas_com_vagas)
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    return jsonify(abrigos), 200


@abrigos_bp.route("/<int:abrigo_id>", methods=["GET"])
def buscar_abrigo(abrigo_id: int):
    """
    GET /abrigos/:id

    Retorna os dados de um abrigo pelo ID, incluindo vagas disponíveis.

    Parâmetro de rota:
        abrigo_id (int): ID do abrigo.

    Retorna:
        200 OK   + dados do abrigo
        404 Not Found se não existir
    """
    try:
        abrigo = AbrigoModel.buscar_por_id(abrigo_id)
    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not abrigo:
        return jsonify({"erro": "Abrigo não encontrado."}), 404

    return jsonify(abrigo), 200
