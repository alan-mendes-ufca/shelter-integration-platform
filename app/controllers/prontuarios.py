"""
Controller: Prontuário

Responsável por orquestrar as rotas HTTP para o prontuário social
(histórico contínuo) das pessoas em situação de rua.
"""

from flask import Blueprint, jsonify, request
from app.models.prontuario import ProntuarioModel
from infra.erros import InternalServerError, NotFoundError

prontuarios_bp = Blueprint("prontuarios", __name__)


@prontuarios_bp.route("", methods=["POST"])
def criar_prontuario():
    prontuario = ProntuarioModel.criar(request.get_json(silent=True))

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
    prontuario_atualizado = ProntuarioModel.atualizar(
        id_pessoa_rua, request.get_json(silent=True)
    )

    if not prontuario_atualizado:
        raise NotFoundError(
            message="Prontuário não encontrado.",
            action="Verifique o ID informado.",
        )

    return jsonify(prontuario_atualizado), 200
