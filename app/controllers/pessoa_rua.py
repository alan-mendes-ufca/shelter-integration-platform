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

# Valores aceitos para o campo nivel_risco — definidos pelo ENUM no banco
NIVEIS_RISCO_VALIDOS = {"baixo", "medio", "alto", "critico"}


@pessoarua_bp.route("", methods=["POST"])
def criar_pessoa():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    try:
        pessoa = PessoaRuaModel.criar(dados)

    except ValueError as err:
        return jsonify({"erro": str(err)}), 400

    except Exception as err:
        return jsonify({"erro": str(err)}), 500

    if not pessoa:
        return jsonify({"erro": "Erro ao criar_pessoa"}), 500

    return jsonify(pessoa), 201


@pessoarua_bp.route("/<int:pessoa_id>", methods=["GET"])
def buscar_por_id(pessoa_id: int):
    try:
        pessoa = PessoaRuaModel.buscar_por_id(pessoa_id)

    except Exception:
        return jsonify({"erro": "Falha ao criar pessoa."}), 500

    if not pessoa:
        return jsonify({"erro": "Pessoa não encontrada."}), 404

    return jsonify(pessoa), 200


@pessoarua_bp.route("", methods=["GET"])
def buscar_por_apelido():
    apelido = request.args.get("apelido", "").strip()
    if not apelido:
        return jsonify({"erro": "Parâmetro 'apelido' é obrigatório"}), 400

    try:
        pessoa = PessoaRuaModel.buscar_por_apelido(apelido)
    except Exception:
        return jsonify({"erro": "Erro interno ao buscar pessoa de rua."}), 500

    return jsonify(pessoa), 200


@pessoarua_bp.route("/<int:pessoa_id>", methods=["PUT"])
def atualizar_pessoa(pessoa_id: int):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "JSON inválido ou ausente."}), 400

    try:
        pessoa_atual = PessoaRuaModel.buscar_por_id(pessoa_id)
        if not pessoa_atual:
            return jsonify({"erro": "Pessoa não encontrada"}), 404

        pessoa = PessoaRuaModel.atualizar(pessoa_id, dados)
    except ValueError as err:
        return jsonify({"erro": str(err)}), 400

    except Exception:
        return jsonify({"erro": "Erro interno ao atualizar pessoa."}), 500

    if not pessoa:
        return jsonify({"erro": "Pessoa não encontrada."}), 404

    return jsonify(pessoa), 200


@pessoarua_bp.route("/<int:pessoa_id>/risco", methods=["PUT"])
def atualizar_risco(pessoa_id: int):
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400

    nivel_risco = dados.get("nivel_risco")
    if not nivel_risco:
        return jsonify({"erro": "Campo 'nivel_risco' é obrigatorio."}), 400

    if nivel_risco not in NIVEIS_RISCO_VALIDOS:
        return (
            jsonify(
                {
                    "erro": "nivel_risco inválido. ",
                    "valores_validos": sorted(NIVEIS_RISCO_VALIDOS),
                }
            ),
            400,
        )

    try:
        pessoa = PessoaRuaModel.atualizar_risco(pessoa_id, nivel_risco)
    except ValueError as err:
        return jsonify({"erro": str(err)}), 400
    except Exception:
        return jsonify({"erro": "Erro interno ao atualizar risco."}), 500

    if not pessoa:
        return jsonify({"erro": "Pessoa não encontrada. "}), 404

    return jsonify(pessoa), 200


@pessoarua_bp.route("/filtros", methods=["GET"])
def listar_pessoas_com_filtros():
    apelido = request.args.get("apelido")
    nome_civil = request.args.get("nome_civil")
    nivel_risco = request.args.get("nivel_risco")
    cpf_opcional = request.args.get("cpf_opcional")

    niveis_validos = {"baixo", "medio", "alto", "critico"}

    if nivel_risco and nivel_risco not in niveis_validos:
        return (
            jsonify(
                {
                    "erro": "nivel_risco inválido. ",
                    "valores_validos": sorted(niveis_validos),
                }
            ),
            400,
        )
    try:
        pessoas = PessoaRuaModel.listar_com_filtros(
            apelido=apelido,
            nome_civil=nome_civil,
            nivel_risco=nivel_risco,
            cpf_opcional=cpf_opcional,
        )
    except Exception:
        return jsonify({"erro": "Erro interno ao listar pessoas com filtros."}), 500

    return jsonify(pessoas), 200
