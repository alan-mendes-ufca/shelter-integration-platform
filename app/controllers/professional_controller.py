"""
Controller: Profissional

Responsável por orquestrar as rotas HTTP para a gestão de profissionais
no sistema, vinculando-os à tabela `pessoa`.
"""

from flask import Blueprint, jsonify, request

from app.models.profissional import ProfissionalModel

profissionais_bp = Blueprint("profissionais", __name__)


@profissionais_bp.route("", methods=["POST"])
def criar_profissional():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    try:
        profissional = ProfissionalModel.criar(dados)
    except ValueError as err:
        return jsonify({"erro": str(err)}), 400
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ou id_pessoa inexistente.", "detalhes": str(err)}
        ), 500

    if not profissional:
        return jsonify({"erro": "Erro ao criar profissional."}), 500

    return jsonify(profissional), 201


@profissionais_bp.route("/<int:profissional_id>", methods=["GET"])
def buscar_por_id(profissional_id: int):
    try:
        profissional = ProfissionalModel.buscar_por_id(profissional_id)
    except Exception:
        return jsonify({"erro": "Falha ao buscar profissional."}), 500

    if not profissional:
        return jsonify({"erro": "Profissional não encontrado."}), 404

    return jsonify(profissional), 201


@profissionais_bp.route("", methods=["GET"])
def listar_profissionais():
    try:
        profissionais = ProfissionalModel.listar()
    except Exception:
        return jsonify({"erro": "Erro interno ao listar profissionais."}), 500

    return jsonify(profissionais), 201
