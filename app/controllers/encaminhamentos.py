from flask import Blueprint, request, jsonify
from app.models.encaminhamento import EncaminhamentoModel

# O prefixo /api/v1/encaminhamentos já é definido no create_app
encaminhamentos_bp = Blueprint("encaminhamentos", __name__)


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
    dados = request.get_json(silent=True)
    resultado = EncaminhamentoModel.criar(dados)
    return jsonify(resultado), 201


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
    encaminhamentos = EncaminhamentoModel.listar_por_pessoa(pessoa_id)
    return jsonify(encaminhamentos), 200


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
    resultado = EncaminhamentoModel.listar_por_status(status)
    return jsonify(resultado), 200


# 4. ATUALIZAR STATUS (PUT)
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
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status_acompanhamento")

    if novo_status == "cancelado":
        resultado = EncaminhamentoModel.cancelar(encaminhamento_id)
    else:
        resultado = EncaminhamentoModel.atualizar_status(encaminhamento_id, novo_status)

    return jsonify(resultado), 200


# 5. CANCELAR ENCAMINHAMENTO (DELETE)
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
    resultado = EncaminhamentoModel.cancelar(encaminhamento_id)
    return jsonify(resultado), 200
