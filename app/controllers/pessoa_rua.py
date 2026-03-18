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

from app.models.pessoa_rua import PessoaRuaModel  # noqa: F401

pessoarua_bp = Blueprint("pessoarua", __name__)


@pessoarua_bp.route("", methods=["POST"])
def criar_pessoa():
    pessoa = PessoaRuaModel.criar(request.get_json(silent=True))

    if not pessoa:
        return jsonify({"erro": "Erro ao criar_pessoa"}), 500

    return jsonify(pessoa), 201


@pessoarua_bp.route("/<int:pessoa_id>", methods=["GET"])
def buscar_por_id(pessoa_id: int):
    pessoa = PessoaRuaModel.buscar_por_id(pessoa_id)

    return jsonify(pessoa), 200


@pessoarua_bp.route("", methods=["GET"])
def buscar_por_apelido():
    pessoa = PessoaRuaModel.buscar_por_apelido(request.args.get("apelido"))

    return jsonify(pessoa), 200


@pessoarua_bp.route("/<int:pessoa_id>", methods=["PUT"])
def atualizar_pessoa(pessoa_id: int):
    pessoa = PessoaRuaModel.atualizar(pessoa_id, request.get_json(silent=True))

    return jsonify(pessoa), 200


@pessoarua_bp.route("/<int:pessoa_id>/risco", methods=["PUT"])
def atualizar_risco(pessoa_id: int):
    dados = request.get_json(silent=True) or {}
    pessoa = PessoaRuaModel.atualizar_risco(pessoa_id, dados.get("nivel_risco"))

    return jsonify(pessoa), 200


@pessoarua_bp.route("/filtros", methods=["GET"])
def listar_pessoas_com_filtros():
    apelido = request.args.get("apelido")
    nome_civil = request.args.get("nome_civil")
    nivel_risco = request.args.get("nivel_risco")
    cpf_opcional = request.args.get("cpf_opcional")

    pessoas = PessoaRuaModel.listar_com_filtros(
        apelido=apelido,
        nome_civil=nome_civil,
        nivel_risco=nivel_risco,
        cpf_opcional=cpf_opcional,
    )

    return jsonify(pessoas), 200
