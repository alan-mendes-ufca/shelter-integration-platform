"""
Controller: PessoaRua
=====================

Estagiário, bem-vindo ao controller. Aqui vivem os endpoints HTTP.

Responsabilidades do controller:
1. Receber a requisição HTTP (método, rota, body, query params).
2. Validar os dados de entrada (campos obrigatórios, formatos, etc.).
3. Chamar o Model correspondente para executar a operação no banco.
4. Retornar a resposta HTTP com o status code correto.

O controller NÃO sabe como funciona o banco de dados. Isso é problema do Model.
O Model NÃO sabe o que é HTTP. Isso é problema do Controller.
Essa separação é o que chamamos de responsabilidade única — e é muito importante.

Tabela de status HTTP que você vai usar muito:
  200 OK              → GET com resultado
  201 Created         → POST com recurso criado com sucesso
  204 No Content      → DELETE bem-sucedido (sem body na resposta)
  400 Bad Request     → Dados inválidos enviados pelo cliente
  404 Not Found       → Recurso não encontrado no banco
  409 Conflict        → Conflito de estado (ex: duplicidade)
  500 Internal Error  → Erro inesperado no servidor (nunca deveria chegar aqui)
"""

from flask import Blueprint, request, jsonify  # noqa: F401
from app.models.pessoa_rua import PessoaRuaModel  # noqa: F401

pessoas_bp = Blueprint("pessoas", __name__, url_prefix="/pessoas")

# Valores aceitos para o campo nivel_risco — definidos pelo ENUM no banco
NIVEIS_RISCO_VALIDOS = {"baixo", "medio", "alto", "critico"}


@pessoas_bp.route("", methods=["POST"])
def criar_pessoa():
    """
    POST /pessoas

    Cria o cadastro provisório de uma pessoa em situação de rua.
    É o PONTO DE ENTRADA obrigatório de toda a jornada no sistema (US01).

    Aceita cadastro sem documentos — apenas apelido + aparência física.
    Isso garante que nenhum atendimento seja bloqueado por burocracia.

    Body JSON esperado:
        {
            "apelido": "João do Chapéu",          (obrigatório)
            "aparencia": "Homem, ~50 anos, ...",  (obrigatório)
            "nome_real": "João Silva",            (opcional)
            "cpf": "123.456.789-00",              (opcional)
            "data_nascimento": "1975-03-10",      (opcional, formato YYYY-MM-DD)
            "genero": "masculino",                (opcional)
            "endereco_ref": "Praça da Sé",        (opcional)
            "nivel_risco": "baixo"                (opcional, default: "baixo")
        }

    Retorna:
        201 Created  + dados da pessoa criada
        400 Bad Request se 'apelido' ou 'aparencia' não forem enviados

    TODO (estagiário): Implemente a validação dos campos obrigatórios e
                       chame PessoaRuaModel.criar(dados).
                       Lembre: request.get_json() retorna None se o Content-Type
                       não for application/json. Trate isso!
    """
    # TODO: Implementar
    # Estrutura esperada:
    #
    # dados = request.get_json()
    # if not dados:
    #     return jsonify({'erro': 'Body JSON inválido ou ausente.'}), 400
    #
    # if not dados.get('apelido') or not dados.get('aparencia'):
    #     return jsonify({'erro': "'apelido' e 'aparencia' são obrigatórios."}), 400
    #
    # pessoa = PessoaRuaModel.criar(dados)
    # return jsonify(pessoa), 201
    return jsonify({"erro": "Endpoint não implementado."}), 501


@pessoas_bp.route("/<int:pessoa_id>", methods=["GET"])
def buscar_pessoa(pessoa_id: int):
    """
    GET /pessoas/:id

    Retorna os dados completos de uma pessoa pelo ID.
    Consultado por profissionais antes de iniciar qualquer atendimento,
    consentimento ou encaminhamento.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa na tabela pessoa_rua.

    Retorna:
        200 OK       + dados da pessoa
        404 Not Found se o ID não existir no banco

    TODO (estagiário): Chame PessoaRuaModel.buscar_por_id(pessoa_id).
                       Se retornar None, devolva 404 com mensagem amigável.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@pessoas_bp.route("", methods=["GET"])
def buscar_por_apelido():
    """
    GET /pessoas?apelido=X

    Busca pessoas por apelido ou características físicas.
    Essencial para EVITAR cadastros duplicados quando a pessoa já foi
    atendida anteriormente.

    Query param:
        apelido (str): Termo de busca (busca parcial com LIKE).

    Retorna:
        200 OK + lista de pessoas (pode ser lista vazia [])
        400 Bad Request se o parâmetro 'apelido' não for enviado

    TODO (estagiário): Use request.args.get('apelido') para pegar o query param.
                       Se vier vazio ou None, retorne 400.
                       Sempre retorne uma lista, mesmo se vazia — nunca retorne None.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@pessoas_bp.route("/<int:pessoa_id>", methods=["PUT"])
def atualizar_pessoa(pessoa_id: int):
    """
    PUT /pessoas/:id

    Atualiza dados da pessoa conforme novas informações são coletadas.
    Ex: descoberta de documentos reais, atualização de endereço de referência.

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa a atualizar.

    Body JSON: qualquer subconjunto dos campos da pessoa (exceto 'nivel_risco',
               que tem endpoint próprio).

    Retorna:
        200 OK       + dados atualizados
        400 Bad Request se o body estiver vazio ou inválido
        404 Not Found se o ID não existir

    TODO (estagiário): Antes de atualizar, busque a pessoa atual com buscar_por_id().
                       Faça merge dos dados existentes com os dados recebidos.
                       Isso garante que campos não enviados não sejam zerados.
                       Depois chame PessoaRuaModel.atualizar(pessoa_id, dados_merged).
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501


@pessoas_bp.route("/<int:pessoa_id>/risco", methods=["PUT"])
def atualizar_risco(pessoa_id: int):
    """
    PUT /pessoas/:id/risco

    Atualiza especificamente o status de vulnerabilidade da pessoa.
    Alimenta decisões de prioridade de intervenção (US06).

    Parâmetro de rota:
        pessoa_id (int): ID da pessoa.

    Body JSON esperado:
        {
            "nivel_risco": "alto"   (obrigatório: "baixo", "medio", "alto" ou "critico")
        }

    Retorna:
        200 OK       + dados atualizados
        400 Bad Request se nivel_risco for inválido ou ausente
        404 Not Found se o ID não existir

    TODO (estagiário): Valide se o valor de nivel_risco está em NIVEIS_RISCO_VALIDOS
                       antes de chamar o model. Devolva 400 com a lista de valores
                       válidos na mensagem de erro — isso ajuda muito o frontend.
    """
    # TODO: Implementar
    return jsonify({"erro": "Endpoint não implementado."}), 501
