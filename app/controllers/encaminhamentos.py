from flask import Blueprint, request, jsonify
from app.models.encaminhamento import EncaminhamentoModel

encaminhamentos_bp = Blueprint("encaminhamentos", __name__)

STATUS_VALIDOS = {"pendente", "atendido", "resolvido", "cancelado"}


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


@encaminhamentos_bp.route("/pessoa-rua/<int:id_pessoa_rua>", methods=["GET"])
def listar_encaminhamentos_pessoa(id_pessoa_rua: int):
    """
    Busca todos os encaminhamentos vinculados a uma pessoa específica (pessoa_rua).
    ---
    tags:
      - Encaminhamentos
    parameters:
      - name: id_pessoa_rua
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lista de encaminhamentos encontrada.
    """
    try:
        encaminhamentos = EncaminhamentoModel.listar_por_pessoa(id_pessoa_rua)
        return jsonify(encaminhamentos), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar histórico: {str(e)}"}), 500


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


@encaminhamentos_bp.route("/<int:encaminhamento_id>/status", methods=["PUT"])
def atualizar_status(encaminhamento_id: int):
    """
    Atualiza o status de um encaminhamento existente.
    ---
    tags:
      - Encaminhamentos
    parameters:
      - name: encaminhamento_id
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
            EncaminhamentoModel.cancelar(encaminhamento_id)
        else:
            EncaminhamentoModel.atualizar_status(encaminhamento_id, novo_status)

        return jsonify({"mensagem": "Status atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao atualizar: {str(e)}"}), 500


@encaminhamentos_bp.route("/<int:encaminhamento_id>", methods=["DELETE"])
def cancelar_encaminhamento(encaminhamento_id: int):
    """
    Cancela um encaminhamento (apenas se estiver com status 'pendente').
    ---
    tags:
      - Encaminhamentos
    parameters:
      - name: encaminhamento_id
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
        resultado = EncaminhamentoModel.cancelar(encaminhamento_id)
        if not resultado:
            return jsonify({"erro": "Operação não permitida ou ID inexistente."}), 409
        return jsonify({"mensagem": "Encaminhamento cancelado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao cancelar: {str(e)}"}), 500
