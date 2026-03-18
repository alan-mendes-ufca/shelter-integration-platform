"""
Controller: Profissional

Responsável por orquestrar as rotas HTTP para a gestão de profissionais
no sistema, vinculando-os à tabela `pessoa`.
"""

from flask import Blueprint, jsonify, request

from app.models.profissional import ProfissionalModel
from infra.erros import InternalServerError, NotFoundError

profissionais_bp = Blueprint("profissionais", __name__)


@profissionais_bp.route("", methods=["POST"])
def criar_profissional():
    profissional = ProfissionalModel.criar(request.get_json(silent=True))

    if not profissional:
        raise InternalServerError(
            message="Erro ao criar profissional.",
            action="Tente novamente mais tarde.",
        )

    return jsonify(profissional), 201


@profissionais_bp.route("/<int:profissional_id>", methods=["GET"])
def buscar_por_id(profissional_id: int):
    profissional = ProfissionalModel.buscar_por_id(profissional_id)

    if not profissional:
        raise NotFoundError(
            message="Profissional não encontrado.",
            action="Verifique o ID informado.",
        )

    return jsonify(profissional), 200


@profissionais_bp.route("", methods=["GET"])
def listar_profissionais():
    profissionais = ProfissionalModel.listar()

    return jsonify(profissionais), 200
