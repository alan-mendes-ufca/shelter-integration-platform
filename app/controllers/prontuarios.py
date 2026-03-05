"""
Controller: Profissional + Prontuario
======================================

Estagiário, juntamos os dois controllers nesse arquivo porque eles são
intimamente relacionados — o Prontuário é o produto final do trabalho
do Profissional e é aqui que a complexidade técnica do sistema aparece.

PROFISSIONAL:
  Endpoints simples de CRUD. Pense no profissional como o "usuário" do sistema.
  Por ora não temos autenticação, mas toda ação registra o profissional_id.

PRONTUÁRIO:
  Aqui fica a lógica mais rica. Antes de qualquer operação no prontuário,
  o controller DEVE verificar se existe consentimento ativo para a pessoa.
  Isso é feito chamando ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id).

  Fluxo de verificação obrigatório (você vai usar isso em vários endpoints):

      consentimento = ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id)
      if not consentimento:
          return jsonify({'erro': 'Pessoa não possui consentimento ativo. Prontuário bloqueado.'}), 403
"""

from flask import Blueprint, request, jsonify  # noqa: F401
from app.models.profissional import ProfissionalModel  # noqa: F401
from app.models.prontuario import ProntuarioModel  # noqa: F401
from app.models.consentimento import ConsentimentoModel  # noqa: F401

# ─── Blueprint: Profissional ───────────────────────────────────────────────────
profissionais_bp = Blueprint('profissionais', __name__, url_prefix='/profissionais')


@profissionais_bp.route('', methods=['POST'])
def criar_profissional():
    """
    POST /profissionais

    Cadastra um novo profissional no sistema (assistente social, educador, etc.).

    Body JSON esperado:
        {
            "nome": "Maria Souza",             (obrigatório)
            "cargo": "Assistente Social",      (obrigatório)
            "email": "maria@creas.gov.br",     (obrigatório, único)
            "registro": "CRESS-SP 12345"       (opcional)
        }

    Retorna:
        201 Created + dados do profissional
        400 Bad Request se campos obrigatórios faltarem
        409 Conflict se o e-mail já estiver cadastrado

    TODO (estagiário): Valide os campos obrigatórios.
                       Envolva ProfissionalModel.criar() num try/except para capturar
                       erros de UNIQUE constraint do banco (e-mail duplicado)
                       e retorne 409 com mensagem amigável.
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


@profissionais_bp.route('/<int:profissional_id>', methods=['GET'])
def buscar_profissional(profissional_id: int):
    """
    GET /profissionais/:id

    Retorna dados do profissional. Usado para exibir o responsável
    em atendimentos e encaminhamentos.

    Parâmetro de rota:
        profissional_id (int): ID do profissional.

    Retorna:
        200 OK + dados do profissional
        404 Not Found se não existir ou estiver inativo

    TODO (estagiário): Chame ProfissionalModel.buscar_por_id(profissional_id).
                       Se retornar None, devolva 404.
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


# ─── Blueprint: Prontuário ─────────────────────────────────────────────────────
prontuarios_bp = Blueprint('prontuarios', __name__, url_prefix='/prontuarios')


@prontuarios_bp.route('', methods=['POST'])
def criar_prontuario():
    """
    POST /prontuarios

    Cria o prontuário social da pessoa.
    SÓ pode ser criado após consentimento válido registrado (US02).

    Body JSON esperado:
        {
            "pessoa_id": 42,                          (obrigatório)
            "diagnostico_social": "Situação de...",   (opcional)
            "observacoes": "Primeiro contato em..."   (opcional)
        }

    Retorna:
        201 Created + prontuário criado
        400 Bad Request se 'pessoa_id' não for enviado
        403 Forbidden se não houver consentimento ativo para a pessoa
        409 Conflict se a pessoa já tiver prontuário

    TODO (estagiário): Fluxo correto:
        1. Valide dados de entrada.
        2. Busque consentimento ativo: ConsentimentoModel.buscar_ativo_por_pessoa(pessoa_id)
        3. Se não tiver → 403 Forbidden (não é 401, pois não é questão de login)
        4. Se tiver → chame ProntuarioModel.criar(pessoa_id, consentimento['id'], dados)
        5. Trate erro de UNIQUE (pessoa já tem prontuário) → 409 Conflict
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


@prontuarios_bp.route('/<int:pessoa_id>', methods=['GET'])
def buscar_prontuario(pessoa_id: int):
    """
    GET /prontuarios/:pessoa_id

    Retorna o prontuário integrado completo (US05).
    Consolida: dados da pessoa, atendimentos, encaminhamentos e status atual.
    BLOQUEADO se não houver consentimento ativo.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa.

    Retorna:
        200 OK + prontuário completo (com atendimentos e encaminhamentos aninhados)
        403 Forbidden se consentimento não estiver ativo
        404 Not Found se o prontuário não existir

    TODO (estagiário): Fluxo:
        1. Verifique consentimento ativo → se não tiver → 403
        2. Chame ProntuarioModel.buscar_completo_por_pessoa(pessoa_id)
        3. Se retornar None → 404
        4. Retorne o prontuário completo com 200
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


@prontuarios_bp.route('/<int:prontuario_id>', methods=['PUT'])
def atualizar_prontuario(prontuario_id: int):
    """
    PUT /prontuarios/:id

    Atualiza informações do prontuário (diagnósticos, observações sociais).
    BLOQUEADO se consentimento for revogado (US03).

    Parâmetro de rota:
        prontuario_id (int): ID do prontuário (não o ID da pessoa!).

    Body JSON:
        {
            "diagnostico_social": "...",  (opcional)
            "observacoes": "..."          (opcional)
        }

    Retorna:
        200 OK + prontuário atualizado
        400 Bad Request se body estiver vazio
        403 Forbidden se consentimento não estiver ativo
        404 Not Found se o prontuário não existir

    TODO (estagiário): Aqui você precisa do pessoa_id para verificar o consentimento,
                       mas a rota recebe prontuario_id. Então:
                       1. Busque o prontuário pelo ID para descobrir o pessoa_id.
                       2. Verifique o consentimento ativo para esse pessoa_id.
                       3. Se revogado → 403.
                       4. Se OK → atualize.
    """
    # TODO: Implementar
    return jsonify({'erro': 'Endpoint não implementado.'}), 501


