"""
Controller: Prontuário

Responsável por orquestrar as rotas HTTP para o prontuário social
(histórico contínuo) das pessoas em situação de rua.
"""

from flask import Blueprint, jsonify, request
from app.models.prontuario import ProntuarioModel
from infra.erros import InternalServerError, NotFoundError, ValidationError

prontuarios_bp = Blueprint("prontuarios", __name__)


@prontuarios_bp.route("", methods=["POST"])
def criar_prontuario():
    dados = request.get_json(silent=True)
    if not dados:
        raise ValidationError(
            message="Body JSON inválido ou ausente.",
            action="Envie um JSON válido no corpo da requisição.",
        )

    try:
        prontuario = ProntuarioModel.criar(dados)
    except ValueError as err:
        raise ValidationError(
            message=str(err),
            action="Revise os dados obrigatórios e tente novamente.",
        ) from err

    if not prontuario:
        raise InternalServerError(
            message="Falha na criação do prontuário.",
            action="Tente novamente mais tarde.",
        )

    return jsonify(prontuario), 201


@prontuarios_bp.route("/<int:id_pessoa_rua>", methods=["GET"])
def buscar_prontuario(id_pessoa_rua: int):
    prontuario = ProntuarioModel.buscar_por_id(id_pessoa_rua)

    if not prontuario:
        raise NotFoundError(
            message="Prontuário não encontrado.",
            action="Verifique o ID informado.",
        )

    return jsonify(prontuario), 200


@prontuarios_bp.route("/<int:id_pessoa_rua>", methods=["PUT"])
def atualizar_prontuario(id_pessoa_rua: int):
    dados = request.get_json(silent=True)
    if not dados:
        raise ValidationError(
            message="Body JSON inválido ou ausente.",
            action="Envie um JSON válido no corpo da requisição.",
        )

    try:
        prontuario_atualizado = ProntuarioModel.atualizar(id_pessoa_rua, dados)
    except PermissionError as err:
        raise ValidationError(
            message=str(err),
            action="Verifique suas permissões e tente novamente.",
        ) from err

    except ValueError as err:
        raise ValidationError(
            message=str(err),
            action="Revise os dados informados e tente novamente.",
        ) from err

    if not prontuario_atualizado:
        raise NotFoundError(
            message="Prontuário não encontrado.",
            action="Verifique o ID informado.",
        )

    return jsonify(prontuario_atualizado), 200
