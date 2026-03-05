"""
Controller: Consentimento
=========================

Estagiário, esse controller é pequeno mas crítico para a conformidade legal.

Lembra das regras do Model? Elas se traduzem assim nos endpoints:

- POST /consentimentos          → cria e "desbloqueia" o prontuário
- GET  /consentimentos/:id      → consulta se o consentimento está ativo
                                  (esse check é feito ANTES de qualquer operação no prontuário)
- PUT  /consentimentos/:id/revogar → bloqueia o prontuário para edição
- GET  /consentimentos/historico/:id → auditoria LGPD

Uma dica de arquitetura: quando um consentimento é revogado (PUT /revogar),
você NÃO precisa fazer nada no prontuário diretamente. O sistema vai consultar
o consentimento antes de mostrar/editar o prontuário — se vier 'ativo=False',
o acesso é bloqueado. Simples e elegante.
"""

from flask import Blueprint, request, jsonify  # noqa: F401
from app.models.consentimento import ConsentimentoModel  # noqa: F401

consentimentos_bp = Blueprint("consentimentos", __name__, url_prefix="/consentimentos")


@consentimentos_bp.route("", methods=["POST"])
def registrar_consentimento():
    """
    POST /consentimentos

    Registra o consentimento formal da pessoa para tratamento de dados.
    Desbloqueia a criação e acesso ao prontuário social (US02).

    Body JSON esperado:
        {
            "pessoa_id": 42,              (obrigatório)
            "observacao": "Explicado..." (opcional)
        }

    Retorna:
        201 Created  + dados do consentimento registrado
        400 Bad Request se 'pessoa_id' não for enviado
        409 Conflict se já existir consentimento ativo para essa pessoa

    TODO (estagiário): Verifique se já existe consentimento ativo antes de criar.
                       Use ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id).
                       Se retornar algo, devolva 409 com mensagem clara.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@consentimentos_bp.route("/<int:pessoa_id>", methods=["GET"])
def verificar_consentimento(pessoa_id: int):
    """
    GET /consentimentos/:pessoa_id

    Verifica se a pessoa possui consentimento ativo.
    Consultado automaticamente antes de qualquer exibição de dados sensíveis.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa.

    Retorna:
        200 OK + { "ativo": true, "consentimento": {...} }  se tiver consentimento ativo
        200 OK + { "ativo": false }                         se não tiver
        (não retorna 404 — a ausência de consentimento é um estado válido)

    TODO (estagiário): Chame ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id).
                       Retorne sempre 200, mas com o campo "ativo" indicando o estado.
                       Quem chama esse endpoint precisa de uma resposta previsível,
                       não de erros inesperados.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@consentimentos_bp.route("/<int:consentimento_id>/revogar", methods=["PUT"])
def revogar_consentimento(consentimento_id: int):
    """
    PUT /consentimentos/:id/revogar

    Registra a revogação do consentimento (US03).

    Após a revogação:
    - O prontuário passa a ser somente leitura.
    - Dados sensíveis ficam ocultos nas respostas da API.
    - Novos atendimentos SIMPLES continuam sendo possíveis.

    Parâmetro de rota:
        consentimento_id (int): ID do consentimento a ser revogado.

    Body JSON (opcional):
        {
            "observacao": "Pessoa solicitou revogação após..." (opcional)
        }

    Retorna:
        200 OK + consentimento atualizado (ativo=False)
        404 Not Found se o consentimento não existir
        409 Conflict se já estiver revogado

    TODO (estagiário): Chame ConsentimentoModel.revogar(consentimento_id, observacao).
                       Se retornar None, o consentimento não existia ou já estava revogado.
                       Diferencie os dois casos se conseguir (404 vs 409).
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@consentimentos_bp.route("/historico/<int:pessoa_id>", methods=["GET"])
def historico_consentimentos(pessoa_id: int):
    """
    GET /consentimentos/historico/:pessoa_id

    Retorna o histórico completo de consentimentos e revogações de uma pessoa.
    Essencial para auditoria e compliance com a LGPD.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa.

    Retorna:
        200 OK + lista de consentimentos em ordem cronológica decrescente
        (lista vazia se a pessoa nunca deu consentimento — isso é válido)

    TODO (estagiário): Chame ConsentimentoModel.historico_por_pessoa(pessoa_id).
                       Sempre retorne uma lista, mesmo vazia.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501
