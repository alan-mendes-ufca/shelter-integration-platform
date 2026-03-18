"""
Controller: Prontuário

Responsável por orquestrar as rotas HTTP para o prontuário social
(histórico contínuo) das pessoas em situação de rua.
"""

from flask import Blueprint, jsonify, request
from app.models.prontuario import ProntuarioModel

prontuarios_bp = Blueprint("prontuarios", __name__)


@prontuarios_bp.route("", methods=["POST"])
def criar_prontuario():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    try:
        prontuario = ProntuarioModel.criar(dados)
    except ValueError as err:
        return jsonify({"erro": str(err)}), 400
    except Exception as err:
        return jsonify({"erro": "Erro ao criar prontuário.", "detalhes": str(err)}), 500

    if not prontuario:
        return jsonify({"erro": "Falha na criação."}), 500

    return jsonify(prontuario), 201


@prontuarios_bp.route("/<int:id_pessoa_rua>", methods=["GET"])
def buscar_prontuario(id_pessoa_rua: int):
    try:
        prontuario = ProntuarioModel.buscar_por_id(id_pessoa_rua)
    except Exception:
        return jsonify({"erro": "Falha ao buscar prontuário."}), 500

    if not prontuario:
        return jsonify({"erro": "Prontuário não encontrado."}), 404

    return jsonify(prontuario), 201


@prontuarios_bp.route("/<int:id_pessoa_rua>", methods=["PUT"])
def atualizar_prontuario(id_pessoa_rua: int):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    try:
        prontuario_atualizado = ProntuarioModel.atualizar(id_pessoa_rua, dados)
        if not prontuario_atualizado:
            return jsonify({"erro": "Prontuário não encontrado."}), 404

    except PermissionError as err:
        return jsonify({"erro": str(err)}), 400

    except ValueError as err:
        return jsonify({"erro": str(err)}), 400

    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao atualizar prontuário.", "detalhes": str(err)}
        ), 500

    return jsonify(prontuario_atualizado), 201
