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

    try:
        abrigo = AbrigoModel.criar(dados)
    except ValueError as err:
        return jsonify({"erro": str(err)}), 400
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao criar abrigo.", "detalhes": str(err)}
        ), 500

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
        return jsonify(
            {"erro": "Erro interno ao listar abrigos.", "detalhes": str(err)}
        ), 500

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
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    pessoa_id = dados.get("pessoa_id")
    abrigo_id = dados.get("abrigo_id")

    if not pessoa_id or not abrigo_id:
        return jsonify(
            {"erro": "Os campos 'pessoa_id' e 'abrigo_id' são obrigatórios."}
        ), 400

    try:
        vaga = VagaModel.registrar_entrada(int(pessoa_id), int(abrigo_id))
    except ValueError as err:
        # Pessoa já acolhida
        return jsonify({"erro": str(err)}), 409
    except RuntimeError as err:
        # Abrigo sem vagas
        return jsonify({"erro": str(err)}), 409
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao registrar entrada.", "detalhes": str(err)}
        ), 500

    return jsonify(vaga), 201


    if not abrigo:
        return jsonify({"erro": "Abrigo não encontrado."}), 404

    return jsonify(abrigo), 200


    Retorna:
        200 + vaga atualizada (status='liberada')
        404 se a vaga não existir
        409 se a saída já tiver sido registrada
    """
    # Busca antes de tentar atualizar para diferenciar 404 de 409
    from app.models.abrigo import VagaModel as VM

    vaga_atual = VM._buscar_por_id(vaga_id)

    if not vaga_atual:
        return jsonify({"erro": "Vaga não encontrada."}), 404

    if vaga_atual["status"] == "liberada":
        return jsonify({"erro": "A saída desta vaga já foi registrada."}), 409

    try:
        vaga = VagaModel.registrar_saida(vaga_id)
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao registrar saída.", "detalhes": str(err)}
        ), 500

    if not vaga:
        return jsonify({"erro": "Não foi possível registrar a saída."}), 500

