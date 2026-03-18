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
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente."}), 400
    pessoa_id = dados.get("pessoa_id")
    if not pessoa_id:
        return jsonify({"erro": "O campo 'pessoa_id' é obrigatório."}), 400

    try:
        consentimento_ativo = ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id)
        if consentimento_ativo:
            return jsonify(
                {"erro": "Conflito: Já existe um consentimento ativo para esta pessoa."}
            ), 409

        consentimento_existente = ConsentimentoModel.buscar_por_pessoa(pessoa_id)

        if consentimento_existente:
            resultado = ConsentimentoModel.reativar_consentimento(
                pessoa_id=pessoa_id, observacao=dados.get("observacao")
            )
        else:
            resultado = ConsentimentoModel.criar(dados)

        # 5. Sucesso absoluto
        return jsonify(resultado), 201

    except ValueError as err:
        return jsonify({"erro": str(err)}), 400

    except Exception as err:
        return jsonify(
            {
                "erro": "Erro interno no servidor ao processar o consentimento.",
                "detalhes": str(err),
            }
        ), 500


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

    # O try protege nossa aplicação caso o banco de dados esteja fora do ar
    try:
        # A sua linha estava certíssima! Ela vai retornar um dicionário ou None
        consentimento_ativo = ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id)

        # Se retornou um dicionário (ou seja, passou nas 3 regras: ID certo, ativo=True e na validade)

        if consentimento_ativo:
            return jsonify({"status": "O consentimento está ativo. "}), 200

        else:
            return jsonify(
                {"status": "Consentimento não está ativo ou não foi criado. "}
            ), 200

    except Exception as err:
        return jsonify(
            {
                "erro": "Erro interno do servidor ao verificar o consentimento. ",
                "detalhes": str(err),
            }
        ), 500


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
    try:
        # 2. Busca o estado real do consentimento (lembrando que consentimento_id = pessoa_id)
        consentimento_atual = ConsentimentoModel.buscar_por_pessoa(consentimento_id)

        # 3. Caso 404: A pessoa nunca assinou um consentimento na vida
        if not consentimento_atual:
            return jsonify({"erro": "Consentimento não encontrado."}), 404

        # 4. Caso 409: O consentimento existe, mas o 'ativo' já é False (já foi revogado)
        # Atenção: no dicionário que volta do MySQL, o False costuma vir como 0
        if not consentimento_atual.get("ativo"):
            return jsonify(
                {"erro": "Conflito: Este consentimento já se encontra revogado."}
            ), 409

        # 5. Caminho feliz: Existe e está ativo! Vamos revogar.
        consentimento_atualizado = ConsentimentoModel.revogar_consentimento(
            pessoa_id=consentimento_id, observacao=observacao
        )

        # 6. Retorna 200 OK com os dados atualizados (agora com ativo=False)
        return jsonify(consentimento_atualizado), 200

    except Exception as err:
        # 7. Proteção contra quedas do banco de dados
        return jsonify(
            {
                "erro": "Erro interno do servidor ao revogar o consentimento.",
                "detalhes": str(err),
            }
        ), 500
