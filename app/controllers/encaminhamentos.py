from flask import Blueprint, request, jsonify
from app.models.encaminhamento import EncaminhamentoModel

# O prefixo /api/v1/encaminhamentos já é definido no create_app
encaminhamentos_bp = Blueprint("encaminhamentos", __name__)

# Status permitidos no sistema
STATUS_VALIDOS = {"pendente", "atendido", "resolvido", "cancelado"}


# 1. CRIAR ENCAMINHAMENTO (POST)
@encaminhamentos_bp.route("", methods=["POST"])
def criar_encaminhamento():
    """
    Cria um encaminhamento vinculado a um atendimento.
    ---
    tags:
      - Encaminhamentos
    parameters:
      - in: body
        name: body
        required: true
        schema:
          required:
            - id_atendimento_fk
            - orgaoDestino
            - motivo
            - prioridade
          properties:
            id_atendimento_fk:
              type: integer
              example: 1
            orgaoDestino:
              type: string
              example: "CRAS Vila Nova"
            motivo:
              type: string
              example: "Necessita de benefício eventual"
            prioridade:
              type: string
              enum: [baixa, media, alta]
              example: "media"
    responses:
      201:
        description: Encaminhamento registrado com sucesso!
    """
    dados = request.get_json()
    campos_obrigatorios = ["id_atendimento_fk", "orgaoDestino", "motivo", "prioridade"]

    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo]:
            return jsonify({"erro": f"O campo '{campo}' é obrigatório."}), 400

    try:
        resultado = EncaminhamentoModel.criar(dados)
        return jsonify(
            {"mensagem": "Encaminhamento registrado com sucesso!", "id": resultado}
        ), 201
    except Exception as e:
        return jsonify({"erro": f"Falha ao salvar: {str(e)}"}), 500


# 2. LISTAR POR PESSOA (GET)
@encaminhamentos_bp.route("/<int:pessoa_id>", methods=["GET"])
def listar_encaminhamentos_pessoa(pessoa_id: int):
    """
    Busca todos os encaminhamentos vinculados a uma pessoa específica.
    ---
    tags:
      - Encaminhamentos
    parameters:
      - name: pessoa_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de encaminhamentos encontrada.
    """
    try:
        encaminhamentos = EncaminhamentoModel.listar_por_pessoa(pessoa_id)
        return jsonify(encaminhamentos), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar histórico: {str(e)}"}), 500


# 3. LISTAR POR STATUS (GET com Query Param)
@encaminhamentos_bp.route("", methods=["GET"])
def listar_por_status():
    """
    Filtra encaminhamentos por status (pendente, atendido, etc).
    ---
    tags:
      - Encaminhamentos
    parameters:
      - name: status
        in: query
        type: string
        required: true
        enum: [pendente, atendido, resolvido, cancelado]
    responses:
      200:
        description: Lista filtrada com sucesso.
    """
    status = request.args.get("status")

    if not status or status not in STATUS_VALIDOS:
        return jsonify(
            {"erro": "Parâmetro 'status' é obrigatório e deve ser válido."}
        ), 400

    try:
        resultado = EncaminhamentoModel.listar_por_status(status)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao filtrar status: {str(e)}"}), 500


# 4. ATUALIZAR STATUS (PUT)
@encaminhamentos_bp.route("/<int:id_encaminhamento_pk>/status", methods=["PUT"])
def atualizar_status(id_encaminhamento_pk: int):
    """
    Atualiza o status de um encaminhamento existente.
    ---
    tags:
      - Encaminhamentos
    parameters:
      - name: id_encaminhamento_pk
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          required:
            - status_acompanhamento
          properties:
            status_acompanhamento:
              type: string
              enum: [pendente, atendido, resolvido, cancelado]
              example: "atendido"
    responses:
      200:
        description: Status atualizado com sucesso.
    """
    dados = request.get_json()
    novo_status = dados.get("status_acompanhamento")

    if not novo_status or novo_status not in STATUS_VALIDOS:
        return jsonify(
            {"erro": "O campo 'status_acompanhamento' é obrigatório ou inválido."}
        ), 400

    try:
        if novo_status == "cancelado":
            EncaminhamentoModel.cancelar(id_encaminhamento_pk)
        else:
            EncaminhamentoModel.atualizar_status(id_encaminhamento_pk, novo_status)

        return jsonify({"mensagem": "Status atualizado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao atualizar: {str(e)}"}), 500


# 5. CANCELAR ENCAMINHAMENTO (DELETE)
@encaminhamentos_bp.route("/<int:id_encaminhamento_pk>", methods=["DELETE"])
def cancelar_encaminhamento(id_encaminhamento_pk: int):
    """
    Cancela um encaminhamento (apenas se estiver com status 'pendente').
    ---
    tags:
      - Encaminhamentos
    parameters:
      - name: id_encaminhamento_pk
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Encaminhamento cancelado com sucesso.
      409:
        description: Não é permitido cancelar um item já processado.
    """
    try:
        EncaminhamentoModel.cancelar(id_encaminhamento_pk)

        return jsonify({"mensagem": "Encaminhamento cancelado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno ao cancelar: {str(e)}"}), 500
