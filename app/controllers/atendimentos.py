"""
Controller: Atendimento
=======================

Estagiário, esse controller vai ser o mais movimentado do sistema no dia a dia.
Todo atendimento de campo — banho, alimentação, escuta — passa por aqui.

Pontos de atenção:
1. O endpoint POST /atendimentos deve funcionar SEMPRE, mesmo sem consentimento.
   Não coloque nenhuma verificação de consentimento aqui. Zero. Nunca.
2. O GET /atendimentos/:pessoa_id lista o histórico — esse SIM pode ser
   consumido pelo prontuário, mas o controller de atendimento em si não faz
   essa verificação. Quem faz é o controller de prontuário.
3. O DELETE /atendimentos/:id é perigoso — em produção, exigiria autenticação
   com papel de gestor. Por enquanto, documente isso mas não bloqueie.
"""

from flask import Blueprint, request, jsonify  # noqa: F401
from app.models.atendimento import AtendimentoModel  # noqa: F401
from infra.erros import ValidationError

atendimentos_bp = Blueprint("atendimentos", __name__, url_prefix="/atendimentos")

# Tipos de atendimento aceitos — espelham o ENUM do banco
TIPOS_ATENDIMENTO_VALIDOS = {
    "escuta",
    "alimentacao",
    "banho",
    "saude",
    "juridico",
    "outro",
}


@atendimentos_bp.route("", methods=["POST"])
def registrar_atendimento():
    """
    POST /atendimentos

    Registra um novo atendimento com tipo, data/hora e profissional responsável.
    SEMPRE possível, independente de consentimento ou prontuário (US04).

    Body JSON esperado:
        {
            "pessoa_id": 42,                     (obrigatório)
            "profissional_id": 7,                (obrigatório)
            "tipo": "escuta",                    (obrigatório: escuta|alimentacao|banho|saude|juridico|outro)
            "unidade": "CREAS Centro",           (obrigatório)
            "observacoes": "Pessoa relatou...",  (opcional)
            "realizado_em": "2026-03-05 14:30"   (opcional, default: agora)
        }

    Retorna:
        201 Created + atendimento registrado
        400 Bad Request se campos obrigatórios faltarem ou 'tipo' for inválido

    TODO (estagiário): Valide todos os campos obrigatórios.
                       Valide se 'tipo' está em TIPOS_ATENDIMENTO_VALIDOS.
                       Inclua a lista de tipos válidos na mensagem de erro caso
                       o tipo enviado seja inválido — ajuda muito o frontend.
    """

    required_fields = {"pessoa_id", "profissional_id", "tipo", "unidade"}

    data = request.get_json()

    if not required_fields.issubset(set(data.keys())):
        raise ValidationError(
            message="Campos obrigatórios faltando ou extras presentes.",
            action="Verifique se 'pessoa_id', 'profissional_id', 'tipo' e 'unidade' estão presentes e sem campos adicionais.",
        )

    if data["tipo"] not in [
        "escuta",
        "alimentacao",
        "banho",
        "saude",
        "juridico",
        "outro",
    ]:
        raise ValidationError(
            message="Campo de 'tipo' preenchido com opção inválida.",
            action="Utilize somente uma das opção a seguir: 'escuta', 'alimentacao', 'banho', 'saude', 'juridico', 'outro'.",
        )

    registered_service = AtendimentoModel.register(data)
    return jsonify(registered_service), 201


@atendimentos_bp.route("/<int:pessoa_id>", methods=["GET"])
def listar_atendimentos_pessoa(pessoa_id: int):
    """
    GET /atendimentos/:pessoa_id

    Lista todos os atendimentos de uma pessoa em ordem cronológica (US05).
    Base do prontuário integrado quando há consentimento ativo.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa.

    Retorna:
        200 OK + lista de atendimentos (com nome do profissional via JOIN)
        (lista vazia se a pessoa nunca foi atendida — isso é válido)

    TODO (estagiário): Chame AtendimentoModel.listar_por_pessoa(pessoa_id).
                       Sempre retorne 200 com lista, mesmo vazia.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@atendimentos_bp.route("", methods=["GET"])
def listar_atendimentos_por_filtro():
    """
    GET /atendimentos?unidade=X&data_inicio=Y&data_fim=Z

    Retorna atendimentos filtrados por unidade e período.
    Usado para gerar estatísticas e relatórios operacionais (US04).

    Query params:
        unidade     (str): Nome ou parte do nome da unidade. (obrigatório)
        data_inicio (str): Data no formato YYYY-MM-DD.       (obrigatório)
        data_fim    (str): Data no formato YYYY-MM-DD.       (obrigatório)

    Retorna:
        200 OK + lista de atendimentos no período
        400 Bad Request se algum parâmetro obrigatório faltar

    TODO (estagiário): Use request.args.get() para capturar os query params.
                       Valide que todos os três foram enviados antes de chamar o model.
                       Não tente validar o formato de data agora — deixe o banco rejeitar
                       e trate o erro genérico com um try/except retornando 400.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@atendimentos_bp.route("/<int:atendimento_id>", methods=["PUT"])
def atualizar_atendimento(atendimento_id: int):
    """
    PUT /atendimentos/:id

    Permite a correção de um atendimento registrado com erro.
    Toda alteração tem registro de auditoria via campo `atualizado_em`.

    Parâmetro de rota:
        atendimento_id (int): ID do atendimento a corrigir.

    Body JSON: qualquer campo do atendimento que precise ser corrigido.

    Retorna:
        200 OK + atendimento atualizado
        400 Bad Request se o body estiver vazio
        404 Not Found se o ID não existir

    TODO (estagiário): Implemente o mesmo padrão de merge de dados do controller
                       de pessoa: busca o estado atual, faz merge com dados novos,
                       depois chama o model para atualizar.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@atendimentos_bp.route("/<int:atendimento_id>", methods=["DELETE"])
def deletar_atendimento(atendimento_id: int):
    """
    DELETE /atendimentos/:id

    Remove um atendimento registrado indevidamente.

    ATENÇÃO DE SEGURANÇA: Em produção, esse endpoint deve exigir autenticação
    com papel de GESTOR. Por enquanto está aberto, mas documente isso como
    débito técnico de segurança a resolver quando implementarmos JWT.

    Parâmetro de rota:
        atendimento_id (int): ID do atendimento a remover.

    Retorna:
        204 No Content → atendimento deletado com sucesso (sem body)
        404 Not Found  → atendimento não encontrado

    TODO (estagiário): 204 No Content significa que não há body na resposta.
                       Em Flask, retorne: return '', 204
                       Não retorne JSON em deletions bem-sucedidas.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501
