"""
Controller: Abrigo + Estadia + VagaCama
=========================================

REGRA DE NEGÓCIO:
- Entrada/saída NÃO requer prontuário, mas requer pessoa cadastrada.
- Consentimento NÃO é verificado aqui. Jamais.

MUDANÇAS em relação à versão anterior (tabela `vaga`):
- POST /vagas/entrada   → agora chama EstadiaModel.registrar_entrada()
- PUT  /vagas/:id/saida → agora chama EstadiaModel.registrar_saida(pessoa_id)
                          o identificador passou de vaga_id para pessoa_id,
                          pois a PK de estadia é (pessoa_id, data_entrada_pk)
- GET  /vagas           → agora aceita filtros por pessoa_id ou abrigo_id
- GET  /abrigos/:id/camas → novo endpoint para ver o status das camas de um abrigo

DÉBITO TÉCNICO:
- Múltiplas queries em sequência sem transação atômica.
"""

from flask import Blueprint, request, jsonify
from app.models.abrigo import AbrigoModel, EstadiaModel, VagaCamaModel

# ─── Blueprint: Abrigo ────────────────────────────────────────────────────────
abrigos_bp = Blueprint("abrigos", __name__, url_prefix="/abrigos")


@abrigos_bp.route("", methods=["POST"])
def criar_abrigo():
    """
    POST /abrigos

    Cadastra um novo abrigo e cria automaticamente todas as camas em vaga_cama.

    Body JSON:
        nome             (str, obrigatório)
        endereco         (str, obrigatório)
        capacidade_total (int, obrigatório, > 0)
        telefone         (str, opcional)

    Retorna:
        201 + abrigo criado
        400 se campos obrigatórios faltarem ou capacidade_total inválida
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
        return jsonify({"erro": "Falha ao criar abrigo."}), 500

    return jsonify(abrigo), 201


@abrigos_bp.route("", methods=["GET"])
def listar_abrigos():
    """
    GET /abrigos
    GET /abrigos?vagas=disponivel

    Lista todos os abrigos ativos.
    Com ?vagas=disponivel, filtra apenas os que têm vagas livres (US07).

    Retorna:
        200 + lista de abrigos
    """
    apenas_com_vagas = request.args.get("vagas") == "disponivel"

    try:
        abrigos = AbrigoModel.listar(apenas_com_vagas=apenas_com_vagas)
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao listar abrigos.", "detalhes": str(err)}
        ), 500

    return jsonify(abrigos), 200


@abrigos_bp.route("/<int:abrigo_id>/camas", methods=["GET"])
def listar_camas(abrigo_id: int):
    """
    GET /abrigos/:id/camas

    Lista todas as camas de um abrigo com seus status ('livre' ou 'ocupada').
    Útil para visualizar a ocupação detalhada de um abrigo específico.

    Parâmetro de rota:
        abrigo_id (int): ID do abrigo.

    Retorna:
        200 + lista de camas com número e status
    """
    try:
        camas = VagaCamaModel.listar_por_abrigo(abrigo_id)
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao listar camas.", "detalhes": str(err)}
        ), 500

    return jsonify(camas), 200


# ─── Blueprint: Vagas (Estadia) ───────────────────────────────────────────────
vagas_bp = Blueprint("vagas", __name__, url_prefix="/vagas")


@vagas_bp.route("/entrada", methods=["POST"])
def registrar_entrada():
    """
    POST /vagas/entrada

    Registra a entrada de uma pessoa em um abrigo, alocando uma cama (US08).

    Body JSON:
        pessoa_id (int, obrigatório) — ID da pessoa_rua
        abrigo_id (int, obrigatório)

    Retorna:
        201 + estadia criada (com numero_cama alocada)
        400 se campos faltarem
        409 se pessoa já estiver acolhida ou abrigo sem camas livres
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
        estadia = EstadiaModel.registrar_entrada(int(pessoa_id), int(abrigo_id))
    except ValueError as err:
        # Pessoa já acolhida
        return jsonify({"erro": str(err)}), 409
    except RuntimeError as err:
        # Sem camas livres
        return jsonify({"erro": str(err)}), 409
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao registrar entrada.", "detalhes": str(err)}
        ), 500

    return jsonify(estadia), 201


@vagas_bp.route("/<int:pessoa_id>/saida", methods=["PUT"])
def registrar_saida(pessoa_id: int):
    """
    PUT /vagas/:pessoa_id/saida

    Registra a saída da pessoa do abrigo, libera a cama e atualiza o contador (US09).

    ATENÇÃO: o identificador na rota agora é pessoa_id (não mais vaga_id),
    pois a PK de estadia é (id_pessoa_rua_fk, data_entrada_pk) e buscamos
    sempre pela estadia ativa da pessoa.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa (pessoa_rua).

    Body JSON (opcional):
        motivo_saida (str): Motivo da saída.

    Retorna:
        200 + estadia encerrada (com data_saida preenchida)
        404 se a pessoa não tiver estadia ativa
    """
    dados = request.get_json(silent=True) or {}
    motivo_saida = dados.get("motivo_saida")

    # Verifica estadia ativa antes de tentar encerrar
    estadia_ativa = EstadiaModel._buscar_ativa_por_pessoa(pessoa_id)
    if not estadia_ativa:
        return jsonify(
            {"erro": "Pessoa não possui estadia ativa em nenhum abrigo."}
        ), 404

    try:
        estadia = EstadiaModel.registrar_saida(pessoa_id, motivo_saida)
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao registrar saída.", "detalhes": str(err)}
        ), 500

    if not estadia:
        return jsonify({"erro": "Não foi possível registrar a saída."}), 500

    return jsonify(estadia), 200


@vagas_bp.route("", methods=["GET"])
def listar_estadias():
    """
    GET /vagas
    GET /vagas?pessoa_id=X
    GET /vagas?abrigo_id=X
    GET /vagas?abrigo_id=X&apenas_ativas=true

    Lista estadias com filtros opcionais.

    Query params:
        pessoa_id    (int): Filtra pelo histórico de uma pessoa específica.
        abrigo_id    (int): Filtra pelas estadias de um abrigo específico.
        apenas_ativas (str): 'true' para retornar só quem está acolhido agora.

    Retorna:
        200 + lista de estadias
        400 se nenhum filtro for enviado
    """
    pessoa_id = request.args.get("pessoa_id", type=int)
    abrigo_id = request.args.get("abrigo_id", type=int)
    apenas_ativas = request.args.get("apenas_ativas", "").lower() == "true"

    if not pessoa_id and not abrigo_id:
        return jsonify(
            {"erro": "Informe ao menos 'pessoa_id' ou 'abrigo_id' como filtro."}
        ), 400

    try:
        if pessoa_id:
            resultado = EstadiaModel.listar_por_pessoa(pessoa_id)
        else:
            resultado = EstadiaModel.listar_por_abrigo(
                abrigo_id, apenas_ativas=apenas_ativas
            )
    except Exception as err:
        return jsonify(
            {"erro": "Erro interno ao listar estadias.", "detalhes": str(err)}
        ), 500

    return jsonify(resultado), 200
