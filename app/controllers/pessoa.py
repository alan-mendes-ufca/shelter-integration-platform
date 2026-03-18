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
from infra.erros import InternalServerError, NotFoundError

pessoa_bp = Blueprint("pessoa", __name__)


@pessoa_bp.route("", methods=["POST"])
def cria_pessoa():
    pessoa = PessoaModel.criar(request.get_json(silent=True))

    if not pessoa:
        raise InternalServerError(
            message="Erro ao criar pessoa.",
            action="Tente novamente mais tarde.",
        )

    return jsonify(pessoa), 201


@pessoa_bp.route("/<int:pessoa_id>", methods=["GET"])
def buscar_por_id(pessoa_id: int):
    pessoa = PessoaModel.buscar_por_id(pessoa_id)

    if not pessoa:
        raise NotFoundError(
            message="Pessoa não encontrada.",
            action="Verifique o ID informado.",
        )

    return jsonify(pessoa), 200


@pessoa_bp.route("", methods=["GET"])
def listar_pessoas():
    pessoas = PessoaModel.listar()

    return jsonify(pessoas), 200


@pessoa_bp.route("/<int:pessoa_id>", methods=["PUT"])
def atualizar_pessoa(pessoa_id: int):
    pessoa = PessoaModel.atualizar(pessoa_id, request.get_json(silent=True))

    if not pessoa:
        raise NotFoundError(
            message="Pessoa não encontrada.",
            action="Verifique o ID informado.",
        )

    return jsonify(pessoa), 200
