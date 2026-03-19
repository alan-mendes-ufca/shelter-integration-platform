"""
Controller: Atendimento

Este arquivo contém os endpoints reponsáveis pelo registro operacional dop dia-a-dia.

Escopo do controller:
- Registrar, atualizar e remover atendimentos
- Listar todos os atendimentos de um determinado paciênte
- Filtrar atendimentos com critérios de unidade de saúde e período

Responsabilidade desta camada:
- interpretar requisições HTTP (body);
- validar entradas básicas de requisição (dado obrigatórios);
- chamar o `AtendimentoModel` para operar os dados;
- retornar respostas HTTP padronizadas com status adequados.

Regras gerais de retorno:
- 201: atendimento registrado
- 200: retornar buscas, atendimento atualizado
- 204: atendimento removido
"""

from flask import Blueprint, request, jsonify
from app.models.atendimento import AtendimentoModel
from app.models.pessoa_rua import PessoaRuaModel
from infra.erros import NotFoundError

atendimentos_bp = Blueprint("atendimentos", __name__, url_prefix="/atendimentos")


@atendimentos_bp.route("", methods=["POST"])
def registrar_atendimento():
    data = request.get_json(silent=True)
    registered_service = AtendimentoModel.registrar(data or {})
    return jsonify(registered_service), 201


@atendimentos_bp.route("/<int:pessoa_id>", methods=["GET"])
def listar_atendimentos_pessoa(pessoa_id: int):
    valid_user = PessoaRuaModel.buscar_por_id(pessoa_id)
    atendimentos_list = AtendimentoModel.listar_por_pessoa(valid_user["id_pessoa_rua"])
    return jsonify(atendimentos_list), 200


@atendimentos_bp.route("", methods=["GET"])
def listar_atendimentos_por_filtro():
    atendimentos = AtendimentoModel.listar_filtrados(request.args)

    return jsonify(atendimentos), 200


@atendimentos_bp.route("/<int:atendimento_id>", methods=["PUT"])
def atualizar_atendimento(atendimento_id: int):
    dados = request.get_json(silent=True)
    atendimento_atualizado = AtendimentoModel.atualizar(atendimento_id, dados or {})

    return jsonify(atendimento_atualizado), 200


@atendimentos_bp.route("/<int:atendimento_id>", methods=["DELETE"])
def deletar_atendimento(atendimento_id: int):
    deletado = AtendimentoModel.deletar(atendimento_id)
    if not deletado:
        raise NotFoundError(
            message="Atendimento não encontrado.",
            action="Verifique o ID informado.",
        )

    return "", 204
