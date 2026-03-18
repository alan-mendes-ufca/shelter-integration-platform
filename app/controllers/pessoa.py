"""
Controller: Pessoa

Este arquivo reúne os endpoints HTTP responsáveis pelo ciclo básico de gestão
de pessoas usuárias do sistema.

Escopo do controller:
- criar cadastro;
- consultar por ID;
- atualizar dados cadastrais;
- listar pessoas cadastradas.

Responsabilidade desta camada:
- interpretar requisições HTTP (path, query e body);
- validar entradas básicas de requisição;
- chamar o `PessoaModel` para acesso a dados;
- retornar respostas HTTP padronizadas com status adequados.

Regras gerais de retorno:
- 200 para consultas/atualizações bem-sucedidas;
- 201 para criação;
- 400 para erro de entrada/validação;
- 404 quando o recurso não existir;
- 500 para falhas inesperadas.

Observação:
As regras de persistência e validações de domínio ligadas ao banco devem ficar
no model. O controller atua como camada de orquestração HTTP.
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
