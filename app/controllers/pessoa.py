"""
Service: Pessoa

Este arquivo reúne as operações de serviço responsáveis pelo ciclo básico de
gestão de pessoas usuárias do sistema.

Escopo do service:
- criar cadastro;
- consultar por ID;
- atualizar dados cadastrais;
- listar pessoas.

Responsabilidade desta camada:
- centralizar regras de negócio da entidade pessoa;
- validar entradas de domínio antes de chamar o model;
- orquestrar chamadas ao `PessoaModel`;
- padronizar mensagens de erro para o controller.

Regras gerais:
- o service não retorna status HTTP;
- erros de validação devem gerar `ValueError`;
- ausência de recurso pode retornar `None` (ou `LookupError`, se adotado no projeto);
- falhas inesperadas devem propagar exceções para tratamento no controller.

Observação:
A persistência e execução de SQL ficam no model.
O service atua como camada intermediária entre controller e model.
"""

from flask import Blueprint, jsonify, request  # noqa: F401

from app.models.pessoa import PessoaModel  # noqa: F401

pessoa_bp = Blueprint("pessoa", __name__)


@pessoa_bp.route("", methods=["POST"])
def cria_pessoa():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente. "}), 400

    try:
        pessoa = PessoaModel.criar(dados)

    except ValueError as err:
        return jsonify({"erro": str(err)}), 400

    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not pessoa:
        return jsonify({"erro": "Erro ao criar pessoa. "}), 500

    return jsonify(pessoa), 201


@pessoa_bp.route("/<int:pessoa_id>", methods=["GET"])
def buscar_por_id(pessoa_id: int):
    try:
        pessoa = PessoaModel.buscar_por_id(pessoa_id)

    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not pessoa:
        return jsonify({"erro": "Pessoa não encontrada."}), 404

    return jsonify(pessoa), 200


@pessoa_bp.route("", methods=["GET"])
def listar_pessoas():
    try:
        pessoas = PessoaModel.listar()

    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    return jsonify(pessoas), 200


@pessoa_bp.route("/<int:pessoa_id>", methods=["PUT"])
def atualizar_pessoa(pessoa_id: int):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "JSON inválido ou ausente."}), 400

    try:
        pessoa_atual = PessoaModel.buscar_por_id(pessoa_id)
        if not pessoa_atual:
            return jsonify({"erro": "Pessoa não encontrada"}), 404

        pessoa = PessoaModel.atualizar(pessoa_id, dados)
    except ValueError as err:
        return jsonify({"erro": str(err)}), 400

    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not pessoa:
        return jsonify({"erro": "Pessoa não encontrada."}), 404

    return jsonify(pessoa), 200
