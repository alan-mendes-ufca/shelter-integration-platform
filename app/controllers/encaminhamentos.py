"""
Controller: Encaminhamento
==========================

Estagiário, esse é o último controller do sistema e fecha o ciclo completo
do fluxo de atendimento: pessoa → consentimento → atendimento → encaminhamento.

O conceito mais importante aqui é a diferença entre os dois tipos:

  FORMAL:     prontuario_id enviado no body → pessoa tem consentimento ativo
              → dados completos → rastreável no histórico do prontuário

  EMERGÊNCIA: prontuario_id não enviado (ou null) → sem consentimento necessário
              → apenas dados mínimos → mas ainda rastreável via atendimento_id

O tipo NÃO é definido pelo frontend — é determinado automaticamente:
    tipo = 'formal' if prontuario_id else 'emergencia'

Isso garante que o sistema nunca aceite um encaminhamento "formal" sem prontuário.

O ciclo de vida do status:
    pendente → atendido → resolvido
    pendente → cancelado (com motivo obrigatório)
"""

from flask import Blueprint, request, jsonify  # noqa: F401
from app.models.encaminhamento import EncaminhamentoModel  # noqa: F401

encaminhamentos_bp = Blueprint('encaminhamentos', __name__, url_prefix='/encaminhamentos')

# Status válidos para o ciclo de vida do encaminhamento
STATUS_VALIDOS = {'pendente', 'atendido', 'resolvido', 'cancelado'}


@encaminhamentos_bp.route('', methods=['POST'])
def criar_encaminhamento():
    """
    POST /encaminhamentos

    Gera um encaminhamento vinculado a um atendimento (US10).

    - Com prontuario_id: encaminhamento FORMAL (dados completos).
    - Sem prontuario_id: encaminhamento de EMERGÊNCIA (dados mínimos).

    Body JSON esperado:
        {
            "atendimento_id": 15,                  (obrigatório)
            "destino": "CRAS Vila Nova",           (obrigatório)
            "motivo": "Necessita de benefício...", (obrigatório)
            "prontuario_id": 8                     (opcional — null = emergência)
        }

    Retorna:
        201 Created + encaminhamento com tipo determinado automaticamente
        400 Bad Request se campos obrigatórios faltarem

    TODO (estagiário): O tipo é determinado aqui no controller, não no model:
                       dados['tipo'] = 'formal' if dados.get('prontuario_id') else 'emergencia'
                       Então passe o dados completo (com 'tipo') para EncaminhamentoModel.criar().
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


@encaminhamentos_bp.route('/<int:pessoa_id>', methods=['GET'])
def listar_encaminhamentos_pessoa(pessoa_id: int):
    """
    GET /encaminhamentos/:pessoa_id

    Lista todos os encaminhamentos de uma pessoa (formais e de emergência).
    Permite ao profissional ver o que já foi solicitado e evitar duplicidade.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa.

    Retorna:
        200 OK + lista de encaminhamentos (pode ser vazia)

    TODO (estagiário): Chame EncaminhamentoModel.listar_por_pessoa(pessoa_id).
                       Sempre retorne 200 com lista, mesmo vazia.
                       Note que a query no model precisa de um JOIN com atendimento
                       para chegar ao pessoa_id — não existe pessoa_id diretamente
                       na tabela encaminhamento.
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


@encaminhamentos_bp.route('', methods=['GET'])
def listar_por_status():
    """
    GET /encaminhamentos?status=pendente

    Filtra encaminhamentos por status. Usado pelo gestor para
    monitorar a resolução dos casos.

    Query param:
        status (str): Um de: pendente | atendido | resolvido | cancelado (obrigatório)

    Retorna:
        200 OK + lista de encaminhamentos com o status informado
        400 Bad Request se o status não for enviado ou for inválido

    TODO (estagiário): Valide o status contra STATUS_VALIDOS antes de chamar o model.
                       Retorne a lista de status válidos na mensagem de erro.
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


@encaminhamentos_bp.route('/<int:encaminhamento_id>/status', methods=['PUT'])
def atualizar_status(encaminhamento_id: int):
    """
    PUT /encaminhamentos/:id/status

    Atualiza o status do encaminhamento no ciclo de vida rastreável.

    Body JSON esperado:
        {
            "status": "atendido",                        (obrigatório)
            "cancelamento_motivo": "Duplicidade..."      (obrigatório APENAS se status='cancelado')
        }

    Retorna:
        200 OK + encaminhamento atualizado
        400 Bad Request se status for inválido ou motivo de cancelamento faltando
        404 Not Found se o encaminhamento não existir

    TODO (estagiário): Regras de validação:
                       1. Valide o status contra STATUS_VALIDOS.
                       2. Se status=='cancelado' e não vier 'cancelamento_motivo', retorne 400.
                          Mensagem sugerida: "O campo 'cancelamento_motivo' é obrigatório para cancelamentos."
                       3. Chame EncaminhamentoModel.atualizar_status() ou cancelar() conforme o caso.
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


@encaminhamentos_bp.route('/<int:encaminhamento_id>', methods=['DELETE'])
def cancelar_encaminhamento(encaminhamento_id: int):
    """
    DELETE /encaminhamentos/:id

    Cancela um encaminhamento emitido indevidamente, registrando o motivo.

    ATENÇÃO: Apesar de ser um DELETE, não apagamos o registro do banco.
    Apenas marcamos como 'cancelado' com o motivo registrado.
    Isso é uma decisão de auditoria — nunca apague histórico de encaminhamentos.

    Parâmetro de rota:
        encaminhamento_id (int): ID do encaminhamento.

    Body JSON esperado:
        {
            "motivo": "Encaminhamento duplicado, gerado por engano."  (obrigatório)
        }

    Retorna:
        200 OK + encaminhamento cancelado (com motivo registrado)
        400 Bad Request se 'motivo' não for enviado
        404 Not Found se não existir
        409 Conflict se já estiver atendido ou resolvido (não pode cancelar)

    TODO (estagiário): Chame EncaminhamentoModel.cancelar(encaminhamento_id, motivo).
                       O model já verifica se o status permite cancelamento.
                       Se retornar None → trate como 404 ou 409 conforme o contexto.
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


