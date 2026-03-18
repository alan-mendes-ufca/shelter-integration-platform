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
from infra.erros import ValidationError

consentimentos_bp = Blueprint("consentimentos", __name__, url_prefix="/consentimentos")


@consentimentos_bp.route("", methods=["POST"])
def registrar_consentimento():
    """
    POST /consentimentos

    Registra o consentimento formal da pessoa para tratamento de dados.
    Desbloqueia a criação e acesso ao prontuário social (US02).

    Body JSON esperado:
        {
            "pessoa_id": 1,              (obrigatório)
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
    dados = request.get_json(silent=True)
    pessoa_id = (dados or {}).get("pessoa_id")

    try:
        consentimento_ativo = ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id)
        if consentimento_ativo:
            return (
                jsonify(
                    {
                        "erro": "Conflito: Já existe um consentimento ativo para esta pessoa."
                    }
                ),
                409,
            )

        consentimento_existente = ConsentimentoModel.buscar_por_pessoa(pessoa_id)

        if consentimento_existente:
            resultado = ConsentimentoModel.reativar_consentimento(
                pessoa_id=pessoa_id, observacao=dados.get("observacao")
            )
        else:
            resultado = ConsentimentoModel.criar(dados)

        # 5. Sucesso absoluto
        return jsonify(resultado), 201

    except ValidationError:
        raise


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

    (estagiário): Chame ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id).
                       Retorne sempre 200, mas com o campo "ativo" indicando o estado.
                       Quem chama esse endpoint precisa de uma resposta previsível,
                       não de erros inesperados.
    """

    consentimento_ativo = ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id)
    if consentimento_ativo:
        return jsonify({"status": "O consentimento está ativo. "}), 200

    return jsonify({"status": "Consentimento não está ativo ou não foi criado. "}), 200


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

    (estagiário): Chame ConsentimentoModel.revogar(consentimento_id, observacao).
                       Se retornar None, o consentimento não existia ou já estava revogado.
                       Diferencie os dois casos se conseguir (404 vs 409).
    """
    dados = request.get_json(silent=True) or {}
    observacao = dados.get("observacao")

    consentimento_atual = ConsentimentoModel.buscar_por_pessoa(consentimento_id)

    if not consentimento_atual:
        return jsonify({"erro": "Consentimento não encontrado."}), 404

    if not consentimento_atual.get("ativo"):
        return (
            jsonify({"erro": "Conflito: Este consentimento já se encontra revogado."}),
            409,
        )

    consentimento_atualizado = ConsentimentoModel.revogar_consentimento(
        pessoa_id=consentimento_id, observacao=observacao
    )

    return jsonify(consentimento_atualizado), 200
