from __future__ import annotations

from flasgger import Swagger


def _schema(ref: str) -> dict[str, str]:
    return {"$ref": f"#/definitions/{ref}"}


def _path_param(name: str, description: str) -> dict:
    return {
        "name": name,
        "in": "path",
        "required": True,
        "type": "integer",
        "description": description,
    }


def _query_param(
    name: str,
    description: str,
    *,
    required: bool = False,
    enum: list[str] | None = None,
) -> dict[str, object]:
    parameter: dict[str, object] = {
        "name": name,
        "in": "query",
        "required": required,
        "type": "string",
        "description": description,
    }
    if enum:
        parameter["enum"] = enum
    return parameter


def _body_param(
    schema_name: str, description: str, *, required: bool = True
) -> dict[str, object]:
    return {
        "name": "body",
        "in": "body",
        "required": required,
        "description": description,
        "schema": _schema(schema_name),
    }


def _response(description: str, schema_name: str | None = None) -> dict[str, object]:
    response: dict[str, object] = {"description": description}
    if schema_name:
        response["schema"] = _schema(schema_name)
    return response


def _array_response(description: str, item_schema_name: str) -> dict:
    return {
        "description": description,
        "schema": {"type": "array", "items": _schema(item_schema_name)},
    }


def _default_responses(*, success: dict, with_bad_request: bool = False) -> dict:
    responses = {
        **success,
        "501": _response("Endpoint ainda não implementado.", "ErrorResponse"),
    }
    if with_bad_request:
        responses["400"] = _response("Requisição inválida.", "ErrorResponse")
    return responses


SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Shelter Integration Platform API",
        "version": "0.1.0",
        "description": (
            "Documentação interativa da API do Sistema Integrado de Atendimento. "
            "Enquanto a implementação funcional evolui, esta spec descreve o contrato "
            "esperado dos endpoints já registrados na aplicação Flask."
        ),
    },
    "basePath": "/api/v1",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {
            "name": "Exemplo",
            "description": "Endpoints simples para smoke tests e exemplos.",
        },
        {
            "name": "Pessoa em Situação de Rua",
            "description": "Cadastro provisório e gestão do nível de risco.",
        },
        {
            "name": "Usuários",
            "description": "Cadastro base de usuários (pessoa).",
        },
        {
            "name": "Consentimentos",
            "description": "Fluxos LGPD de consentimento e revogação.",
        },
        {
            "name": "Atendimentos",
            "description": "Registros operacionais do atendimento diário.",
        },
        {
            "name": "Profissionais",
            "description": "Cadastro de profissionais que operam o sistema.",
        },
        {
            "name": "Prontuários",
            "description": "Consulta consolidada e atualização do prontuário social.",
        },
        {
            "name": "Abrigos",
            "description": "Cadastro e consulta da rede de acolhimento.",
        },
        {
            "name": "Vagas",
            "description": "Entradas e saídas em abrigos com controle de capacidade.",
        },
        {
            "name": "Encaminhamentos",
            "description": "Fluxo de encaminhamentos.",
        },
    ],
    "definitions": {
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "erro": {"type": "string", "example": "Endpoint não implementado."}
            },
            "required": ["erro"],
        },
        "HelloResponse": {
            "type": "object",
            "properties": {"message": {"type": "string", "example": "Hello, World!"}},
            "required": ["message"],
        },
        "Pessoa": {
            "type": "object",
            "properties": {
                "id_pessoa_rua": {"type": "integer", "example": 42},
                "apelido": {"type": "string", "example": "João do Chapéu"},
                "descricao_fisica": {
                    "type": "string",
                    "example": "Homem, cerca de 50 anos",
                },
                "nome_civil": {"type": "string", "example": "João Silva"},
                "cpf_opcional": {"type": "string", "example": "39053344705"},
                "nivel_risco": {
                    "type": "string",
                    "enum": ["baixo", "medio", "alto", "critico"],
                    "example": "alto",
                },
            },
        },
        "PessoaCreateInput": {
            "type": "object",
            "required": ["apelido", "descricao_fisica"],
            "properties": {
                "apelido": {"type": "string", "example": "João do Chapéu"},
                "descricao_fisica": {
                    "type": "string",
                    "example": "Homem, cerca de 50 anos, chapéu preto",
                },
                "nome_civil": {"type": "string"},
                "cpf_opcional": {"type": "string", "example": "39053344705"},
            },
        },
        "PessoaUpdateInput": {
            "type": "object",
            "properties": {
                "apelido": {"type": "string"},
                "descricao_fisica": {"type": "string"},
                "nome_civil": {"type": "string"},
                "cpf_opcional": {"type": "string"},
            },
        },
        "PessoaRiscoInput": {
            "type": "object",
            "required": ["nivel_risco"],
            "properties": {
                "nivel_risco": {
                    "type": "string",
                    "enum": ["baixo", "medio", "alto", "critico"],
                    "example": "critico",
                }
            },
        },
        "Usuario": {
            "type": "object",
            "properties": {
                "id_pessoa": {"type": "integer", "example": 1},
                "nome": {"type": "string", "example": "Maria Souza"},
                "senha": {"type": "string", "example": "senha123"},
            },
        },
        "UsuarioCreateInput": {
            "type": "object",
            "required": ["nome", "senha"],
            "properties": {
                "nome": {"type": "string", "example": "Maria Souza"},
                "senha": {"type": "string", "example": "senha123"},
            },
        },
        "UsuarioUpdateInput": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "example": "Maria Souza"},
                "senha": {"type": "string", "example": "novaSenha123"},
            },
        },
        "Consentimento": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 8},
                "pessoa_id": {"type": "integer", "example": 42},
                "ativo": {"type": "boolean", "example": True},
                "observacao": {
                    "type": "string",
                    "example": "Explicado o uso dos dados.",
                },
            },
        },
        "ConsentimentoCreateInput": {
            "type": "object",
            "required": ["pessoa_id"],
            "properties": {
                "pessoa_id": {"type": "integer", "example": 42},
                "observacao": {
                    "type": "string",
                    "example": "Pessoa concordou com o tratamento dos dados.",
                },
            },
        },
        "ConsentimentoRevogacaoInput": {
            "type": "object",
            "properties": {
                "observacao": {
                    "type": "string",
                    "example": "Pessoa solicitou revogação após nova orientação.",
                }
            },
        },
        "ConsentimentoStatusResponse": {
            "type": "object",
            "properties": {
                "ativo": {"type": "boolean", "example": True},
                "consentimento": _schema("Consentimento"),
            },
            "required": ["ativo"],
        },
        "Atendimento": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 15},
                "pessoa_id": {"type": "integer", "example": 42},
                "profissional_id": {"type": "integer", "example": 7},
                "tipo": {
                    "type": "string",
                    "enum": [
                        "escuta",
                        "alimentacao",
                        "banho",
                        "saude",
                        "juridico",
                        "outro",
                    ],
                    "example": "escuta",
                },
                "unidade": {"type": "string", "example": "CREAS Centro"},
                "observacoes": {
                    "type": "string",
                    "example": "Pessoa relatou necessidade de benefício.",
                },
                "realizado_em": {"type": "string", "example": "2026-03-05 14:30"},
            },
        },
        "AtendimentoCreateInput": {
            "type": "object",
            "required": ["pessoa_id", "profissional_id", "tipo", "unidade"],
            "properties": {
                "pessoa_id": {"type": "integer", "example": 42},
                "profissional_id": {"type": "integer", "example": 7},
                "tipo": {
                    "type": "string",
                    "enum": [
                        "escuta",
                        "alimentacao",
                        "banho",
                        "saude",
                        "juridico",
                        "outro",
                    ],
                    "example": "alimentacao",
                },
                "unidade": {"type": "string", "example": "CREAS Centro"},
                "observacoes": {"type": "string"},
                "realizado_em": {"type": "string", "example": "2026-03-05 14:30"},
            },
        },
        "AtendimentoUpdateInput": {
            "type": "object",
            "properties": {
                "tipo": {
                    "type": "string",
                    "enum": [
                        "escuta",
                        "alimentacao",
                        "banho",
                        "saude",
                        "juridico",
                        "outro",
                    ],
                },
                "unidade": {"type": "string"},
                "observacoes": {"type": "string"},
                "realizado_em": {"type": "string"},
            },
        },
        "Profissional": {
            "type": "object",
            "properties": {
                "id_profissional": {"type": "integer", "example": 1},
                "id_pessoa": {"type": "integer", "example": 1},
                "nome": {"type": "string", "example": "Maria Souza"},
                "cargo": {"type": "string", "example": "assistente_social"},
                "registro_conselho": {"type": "string", "example": "CRESS-SP 12345"},
            },
        },
        "ProfissionalCreateInput": {
            "type": "object",
            "required": ["id_pessoa", "cargo"],
            "properties": {
                "id_pessoa": {"type": "integer", "example": 1},
                "cargo": {"type": "string", "example": "assistente_social"},
                "registro_conselho": {"type": "string", "example": "CRESS-SP 12345"},
            },
        },
        "Prontuario": {
            "type": "object",
            "properties": {
                "id_pessoa_rua": {"type": "integer", "example": 1},
                "id_consentimento": {"type": "integer", "example": 1},
                "id_profissional": {"type": "integer", "example": 1},
                "data_criacao": {"type": "string", "example": "2026-03-17 23:54:00"},
                "resumo_historico": {
                    "type": "string",
                    "example": "Primeiro atendimento realizado. O indivíduo aceitou o acolhimento.",
                },
                "apelido": {"type": "string", "example": "João do Chapéu"},
                "grau_vulnerabilidade": {"type": "string", "example": "alto"},
            },
        },
        "ProntuarioCreateInput": {
            "type": "object",
            "required": ["id_pessoa_rua", "id_consentimento", "id_profissional"],
            "properties": {
                "id_pessoa_rua": {"type": "integer", "example": 1},
                "id_consentimento": {"type": "integer", "example": 1},
                "id_profissional": {"type": "integer", "example": 1},
                "resumo_historico": {
                    "type": "string",
                    "example": "Primeiro atendimento realizado.",
                },
            },
        },
        "ProntuarioUpdateInput": {
            "type": "object",
            "properties": {
                "resumo_historico": {
                    "type": "string",
                    "example": "Paciente apresentou melhora no quadro.",
                },
                "id_profissional": {"type": "integer", "example": 2},
                "id_consentimento": {"type": "integer", "example": 1},
                "grau_vulnerabilidade": {
                    "type": "string",
                    "enum": ["baixo", "medio", "alto", "critico"],
                    "example": "baixo",
                },
            },
        },
        "Abrigo": {
            "type": "object",
            "properties": {
                "id_abrigo": {"type": "integer", "example": 3},
                "nome": {"type": "string", "example": "Abrigo Esperança"},
                "endereco": {"type": "string", "example": "Rua das Flores, 100"},
                "capacidade_total": {"type": "integer", "example": 50},
                "vagas_disponiveis": {"type": "integer", "example": 12},
                "telefone": {"type": "string", "example": "(85) 9999-9999"},
                "ativo": {"type": "boolean", "example": True},
            },
        },
        "AbrigoCreateInput": {
            "type": "object",
            "required": ["nome", "endereco", "capacidade_total"],
            "properties": {
                "nome": {"type": "string", "example": "Abrigo Esperança"},
                "endereco": {"type": "string", "example": "Rua das Flores, 100"},
                "capacidade_total": {"type": "integer", "minimum": 1, "example": 50},
                "telefone": {"type": "string", "example": "(85) 9999-9999"},
            },
        },
        # ── Vaga Cama ─────────────────────────────────────────────────────────
        "VagaCama": {
            "type": "object",
            "properties": {
                "numero_cama_pk": {"type": "integer", "example": 3},
                "id_abrigo_fk": {"type": "integer", "example": 1},
                "status": {
                    "type": "string",
                    "enum": ["livre", "ocupada"],
                    "example": "ocupada",
                },
            },
        },
        # ── Estadia ───────────────────────────────────────────────────────────
        "Estadia": {
            "type": "object",
            "properties": {
                "id_pessoa_rua_fk": {"type": "integer", "example": 42},
                "data_entrada_pk": {"type": "string", "example": "2026-03-18 20:49:53"},
                "numero_cama_fk": {"type": "integer", "example": 3},
                "id_abrigo_fk": {"type": "integer", "example": 1},
                "data_saida": {"type": "string", "example": "2026-03-19 08:00:00"},
                "motivo_saida": {
                    "type": "string",
                    "example": "Transferido para outro abrigo",
                },
            },
        },
        "EstadiaEntradaInput": {
            "type": "object",
            "required": ["pessoa_id", "abrigo_id"],
            "properties": {
                "pessoa_id": {"type": "integer", "example": 42},
                "abrigo_id": {"type": "integer", "example": 1},
            },
        },
        "EstadiaSaidaInput": {
            "type": "object",
            "required": ["numero_cama", "abrigo_id"],
            "properties": {
                "numero_cama": {"type": "integer", "example": 3},
                "abrigo_id": {"type": "integer", "example": 1},
                "motivo_saida": {
                    "type": "string",
                    "example": "Transferido para outro abrigo",
                },
            },
        },
    },
    "paths": {
        "/hello": {
            "get": {
                "tags": ["Exemplo"],
                "summary": "Retorna uma saudação simples.",
                "description": "Endpoint de exemplo útil para smoke tests rápidos da aplicação.",
                "parameters": [
                    _query_param("name", "Nome opcional para personalizar a mensagem.")
                ],
                "responses": {
                    "200": _response("Saudação gerada com sucesso.", "HelloResponse")
                },
            }
        },
        "/pessoas": {
            "post": {
                "tags": ["Usuários"],
                "summary": "Cria um usuário (pessoa).",
                "parameters": [
                    _body_param(
                        "UsuarioCreateInput",
                        "Dados obrigatórios para cadastro de pessoa.",
                    )
                ],
                "responses": _default_responses(
                    success={"201": _response("Pessoa criada com sucesso.", "Usuario")},
                    with_bad_request=True,
                ),
            },
            "get": {
                "tags": ["Usuários"],
                "summary": "Lista usuários cadastrados.",
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de pessoas retornada com sucesso.", "Usuario"
                        )
                    }
                ),
            },
        },
        "/pessoas/{pessoa_id}": {
            "get": {
                "tags": ["Usuários"],
                "summary": "Busca um usuário por ID.",
                "parameters": [_path_param("pessoa_id", "ID da pessoa cadastrada.")],
                "responses": _default_responses(
                    success={
                        "200": _response("Pessoa encontrada.", "Usuario"),
                        "404": _response("Pessoa não encontrada.", "ErrorResponse"),
                    }
                ),
            },
            "put": {
                "tags": ["Usuários"],
                "summary": "Atualiza dados de um usuário.",
                "parameters": [
                    _path_param("pessoa_id", "ID da pessoa a atualizar."),
                    _body_param(
                        "UsuarioUpdateInput", "Campos permitidos para atualização."
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Pessoa atualizada com sucesso.", "Usuario"),
                        "404": _response("Pessoa não encontrada.", "ErrorResponse"),
                    },
                    with_bad_request=True,
                ),
            },
        },
        "/pessoarua": {
            "post": {
                "tags": ["Pessoa em Situação de Rua"],
                "summary": "Cria o cadastro provisório de uma pessoa.",
                "description": (
                    "Ponto de entrada obrigatório da jornada da pessoa no sistema. "
                    "Por padrão, o nível de risco é definido como 'medio'. "
                    "Se quiser alterar, use o endpoint PUT /pessoarua/{id_pessoa_rua}/risco."
                ),
                "parameters": [
                    _body_param(
                        "PessoaCreateInput", "Dados mínimos para o cadastro provisório."
                    )
                ],
                "responses": _default_responses(
                    success={"201": _response("Pessoa criada com sucesso.", "Pessoa")},
                    with_bad_request=True,
                ),
            },
            "get": {
                "tags": ["Pessoa em Situação de Rua"],
                "summary": "Busca pessoas por apelido.",
                "parameters": [
                    _query_param(
                        "apelido",
                        "Termo de busca por apelido ou características físicas.",
                        required=True,
                    )
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response("Lista de pessoas encontrada.", "Pessoa")
                    },
                    with_bad_request=True,
                ),
            },
        },
        "/pessoarua/{id_pessoa_rua}": {
            "get": {
                "tags": ["Pessoa em Situação de Rua"],
                "summary": "Retorna uma pessoa pelo ID.",
                "parameters": [
                    _path_param("id_pessoa_rua", "ID da pessoa em situação de rua.")
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Pessoa encontrada.", "Pessoa"),
                        "404": _response("Pessoa não encontrada.", "ErrorResponse"),
                    }
                ),
            },
            "put": {
                "tags": ["Pessoa em Situação de Rua"],
                "summary": "Atualiza dados de uma pessoa.",
                "parameters": [
                    _path_param(
                        "id_pessoa_rua", "ID da pessoa em situação de rua a atualizar."
                    ),
                    _body_param("PessoaUpdateInput", "Campos a serem atualizados."),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Pessoa atualizada com sucesso.", "Pessoa"),
                        "404": _response("Pessoa não encontrada.", "ErrorResponse"),
                    },
                    with_bad_request=True,
                ),
            },
        },
        "/pessoarua/{id_pessoa_rua}/risco": {
            "put": {
                "tags": ["Pessoa em Situação de Rua"],
                "summary": "Atualiza o nível de risco da pessoa.",
                "parameters": [
                    _path_param(
                        "id_pessoa_rua", "ID da pessoa em situação de rua a atualizar."
                    ),
                    _body_param("PessoaRiscoInput", "Novo nível de risco da pessoa."),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Nível de risco atualizado.", "Pessoa"),
                        "404": _response("Pessoa não encontrada.", "ErrorResponse"),
                    },
                    with_bad_request=True,
                ),
            }
        },
        "/pessoarua/filtros": {
            "get": {
                "tags": ["Pessoa em Situação de Rua"],
                "summary": "Lista pessoas com filtros opcionais.",
                "parameters": [
                    _query_param("apelido", "Filtro parcial por apelido."),
                    _query_param("nome_civil", "Filtro parcial por nome civil."),
                    _query_param(
                        "nivel_risco",
                        "Filtro por nível de risco.",
                        enum=["baixo", "medio", "alto", "critico"],
                    ),
                    _query_param(
                        "cpf_opcional",
                        "Filtro por CPF opcional (com ou sem máscara).",
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de pessoas filtrada com sucesso.", "Pessoa"
                        )
                    },
                    with_bad_request=True,
                ),
            }
        },
        "/consentimentos": {
            "post": {
                "tags": ["Consentimentos"],
                "summary": "Registra o consentimento formal de uma pessoa.",
                "parameters": [
                    _body_param(
                        "ConsentimentoCreateInput",
                        "Dados necessários para o consentimento.",
                    )
                ],
                "responses": _default_responses(
                    success={
                        "201": _response(
                            "Consentimento registrado com sucesso.", "Consentimento"
                        ),
                        "409": _response(
                            "Já existe consentimento ativo para a pessoa.",
                            "ErrorResponse",
                        ),
                    },
                    with_bad_request=True,
                ),
            },
        },
        "/consentimentos/{pessoa_id}": {
            "get": {
                "tags": ["Consentimentos"],
                "summary": "Verifica se a pessoa possui consentimento ativo.",
                "parameters": [_path_param("pessoa_id", "ID da pessoa consultada.")],
                "responses": _default_responses(
                    success={
                        "200": _response(
                            "Estado atual do consentimento.",
                            "ConsentimentoStatusResponse",
                        )
                    }
                ),
            }
        },
        "/consentimentos/{consentimento_id}/revogar": {
            "put": {
                "tags": ["Consentimentos"],
                "summary": "Revoga um consentimento existente.",
                "parameters": [
                    _path_param("consentimento_id", "ID do consentimento a revogar."),
                    _body_param(
                        "ConsentimentoRevogacaoInput",
                        "Observação opcional da revogação.",
                        required=False,
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response(
                            "Consentimento revogado com sucesso.", "Consentimento"
                        ),
                        "404": _response(
                            "Consentimento não encontrado.", "ErrorResponse"
                        ),
                        "409": _response("Consentimento já revogado.", "ErrorResponse"),
                    }
                ),
            }
        },
        "/consentimentos/historico/{pessoa_id}": {
            "get": {
                "tags": ["Consentimentos"],
                "summary": "Lista o histórico de consentimentos de uma pessoa.",
                "parameters": [_path_param("pessoa_id", "ID da pessoa consultada.")],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Histórico encontrado com sucesso.", "Consentimento"
                        )
                    }
                ),
            }
        },
        "/atendimentos": {
            "post": {
                "tags": ["Atendimentos"],
                "summary": "Registra um novo atendimento.",
                "description": "Pode ser usado mesmo sem consentimento ou prontuário.",
                "parameters": [
                    _body_param(
                        "AtendimentoCreateInput", "Dados do atendimento realizado."
                    )
                ],
                "responses": _default_responses(
                    success={
                        "201": _response(
                            "Atendimento registrado com sucesso.", "Atendimento"
                        )
                    },
                    with_bad_request=True,
                ),
            },
            "get": {
                "tags": ["Atendimentos"],
                "summary": "Filtra atendimentos por unidade e período.",
                "parameters": [
                    _query_param(
                        "unidade", "Nome ou parte do nome da unidade.", required=True
                    ),
                    _query_param(
                        "data_inicio",
                        "Data inicial no formato YYYY-MM-DD.",
                        required=True,
                    ),
                    _query_param(
                        "data_fim", "Data final no formato YYYY-MM-DD.", required=True
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Atendimentos filtrados com sucesso.", "Atendimento"
                        )
                    },
                    with_bad_request=True,
                ),
            },
        },
        "/atendimentos/{id}": {
            "get": {
                "tags": ["Atendimentos"],
                "summary": "Lista atendimentos de uma pessoa.",
                "description": "Nesta operação, o parâmetro `id` representa o `pessoa_id`.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID da pessoa cujos atendimentos serão listados.",
                    }
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Histórico de atendimentos retornado com sucesso.",
                            "Atendimento",
                        )
                    }
                ),
            },
            "put": {
                "tags": ["Atendimentos"],
                "summary": "Atualiza um atendimento existente.",
                "description": "Nesta operação, o parâmetro `id` representa o `atendimento_id`.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID do atendimento a ser corrigido.",
                    },
                    _body_param(
                        "AtendimentoUpdateInput", "Campos que precisam ser corrigidos."
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response(
                            "Atendimento atualizado com sucesso.", "Atendimento"
                        ),
                        "404": _response(
                            "Atendimento não encontrado.", "ErrorResponse"
                        ),
                    },
                    with_bad_request=True,
                ),
            },
            "delete": {
                "tags": ["Atendimentos"],
                "summary": "Remove um atendimento registrado indevidamente.",
                "description": "Em produção, esta operação deverá exigir autenticação de gestor.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID do atendimento a remover.",
                    }
                ],
                "responses": _default_responses(
                    success={
                        "204": {"description": "Atendimento removido com sucesso."},
                        "404": _response(
                            "Atendimento não encontrado.", "ErrorResponse"
                        ),
                    }
                ),
            },
        },
        "/profissionais": {
            "post": {
                "tags": ["Profissionais"],
                "summary": "Cadastra um profissional no sistema.",
                "parameters": [
                    _body_param("ProfissionalCreateInput", "Dados do profissional.")
                ],
                "responses": _default_responses(
                    success={
                        "201": _response(
                            "Profissional criado com sucesso.", "Profissional"
                        ),
                    },
                    with_bad_request=True,
                ),
            },
            "get": {
                "tags": ["Profissionais"],
                "summary": "Lista profissionais cadastrados.",
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de profissionais retornada com sucesso.",
                            "Profissional",
                        )
                    }
                ),
            },
        },
        "/profissionais/{profissional_id}": {
            "get": {
                "tags": ["Profissionais"],
                "summary": "Retorna os dados de um profissional.",
                "parameters": [
                    _path_param("profissional_id", "ID do profissional consultado.")
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Profissional encontrado.", "Profissional"),
                        "404": _response(
                            "Profissional não encontrado.", "ErrorResponse"
                        ),
                    }
                ),
            }
        },
        "/prontuarios": {
            "post": {
                "tags": ["Prontuários"],
                "summary": "Cria um prontuário social.",
                "description": "Disponível somente para pessoas com consentimento ativo.",
                "parameters": [
                    _body_param(
                        "ProntuarioCreateInput", "Dados iniciais do prontuário."
                    )
                ],
                "responses": _default_responses(
                    success={
                        "201": _response(
                            "Prontuário criado com sucesso.", "Prontuario"
                        ),
                        "403": _response(
                            "Pessoa sem consentimento ativo.", "ErrorResponse"
                        ),
                        "409": _response(
                            "Pessoa já possui prontuário.", "ErrorResponse"
                        ),
                    },
                    with_bad_request=True,
                ),
            }
        },
        "/prontuarios/{id_pessoa_rua}": {
            "get": {
                "tags": ["Prontuários"],
                "summary": "Retorna o prontuário integrado de uma pessoa.",
                "parameters": [
                    {
                        "name": "id_pessoa_rua",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID da pessoa dona do prontuário.",
                    }
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Prontuário encontrado.", "Prontuario"),
                        "404": _response("Prontuário não encontrado.", "ErrorResponse"),
                    }
                ),
            },
            "put": {
                "tags": ["Prontuários"],
                "summary": "Atualiza um prontuário existente.",
                "parameters": [
                    {
                        "name": "id_pessoa_rua",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID da pessoa em situação de rua.",
                    },
                    _body_param(
                        "ProntuarioUpdateInput",
                        "Campos do prontuário que serão alterados.",
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response(
                            "Prontuário atualizado com sucesso.", "Prontuario"
                        ),
                        "403": _response(
                            "Consentimento revogado ou inexistente.", "ErrorResponse"
                        ),
                        "404": _response("Prontuário não encontrado.", "ErrorResponse"),
                    },
                    with_bad_request=True,
                ),
            },
        },
        # ── Abrigos ───────────────────────────────────────────────────────────
        "/abrigos": {
            "post": {
                "tags": ["Abrigos"],
                "summary": "Cadastra um abrigo no sistema.",
                "description": (
                    "Ao cadastrar, todas as camas são criadas automaticamente "
                    "em vaga_cama com status 'livre'."
                ),
                "parameters": [
                    _body_param("AbrigoCreateInput", "Dados de cadastro do abrigo.")
                ],
                "responses": _default_responses(
                    success={"201": _response("Abrigo criado com sucesso.", "Abrigo")},
                    with_bad_request=True,
                ),
            },
            "get": {
                "tags": ["Abrigos"],
                "summary": "Lista abrigos ativos.",
                "parameters": [
                    _query_param(
                        "vagas",
                        "Use 'disponivel' para filtrar apenas abrigos com vagas livres.",
                        enum=["disponivel"],
                    )
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de abrigos retornada com sucesso.", "Abrigo"
                        )
                    }
                ),
            },
        },
        "/abrigos/{abrigo_id}/camas": {
            "get": {
                "tags": ["Abrigos"],
                "summary": "Lista as camas de um abrigo com seus status.",
                "description": "Retorna todas as camas do abrigo indicando quais estão livres ou ocupadas.",
                "parameters": [_path_param("abrigo_id", "ID do abrigo.")],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de camas retornada com sucesso.", "VagaCama"
                        )
                    }
                ),
            }
        },
        # ── Vagas (Estadia) ───────────────────────────────────────────────────
        "/vagas/entrada": {
            "post": {
                "tags": ["Vagas"],
                "summary": "Registra a entrada de uma pessoa em um abrigo.",
                "description": (
                    "Aloca automaticamente a primeira cama livre do abrigo. "
                    "Não requer prontuário ou consentimento."
                ),
                "parameters": [
                    _body_param(
                        "EstadiaEntradaInput", "Pessoa e abrigo para o acolhimento."
                    )
                ],
                "responses": _default_responses(
                    success={
                        "201": _response("Entrada registrada com sucesso.", "Estadia"),
                        "409": _response(
                            "Sem camas disponíveis ou pessoa já acolhida.",
                            "ErrorResponse",
                        ),
                    },
                    with_bad_request=True,
                ),
            }
        },
        "/vagas/saida": {
            "put": {
                "tags": ["Vagas"],
                "summary": "Registra a saída de uma pessoa pelo número da cama.",
                "description": (
                    "Identifica a estadia ativa pela cama e abrigo informados, "
                    "registra a saída, libera a cama e incrementa o contador de vagas."
                ),
                "parameters": [
                    _body_param(
                        "EstadiaSaidaInput",
                        "Número da cama, abrigo e motivo opcional da saída.",
                    )
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Saída registrada com sucesso.", "Estadia"),
                        "404": _response(
                            "Nenhuma estadia ativa para essa cama.", "ErrorResponse"
                        ),
                    },
                    with_bad_request=True,
                ),
            }
        },
        "/vagas": {
            "get": {
                "tags": ["Vagas"],
                "summary": "Lista estadias com filtros opcionais.",
                "description": (
                    "Informe ao menos 'pessoa_id' ou 'abrigo_id'. "
                    "Use 'apenas_ativas=true' para ver só quem está acolhido agora."
                ),
                "parameters": [
                    _query_param("pessoa_id", "Filtra pelo histórico de uma pessoa."),
                    _query_param("abrigo_id", "Filtra pelas estadias de um abrigo."),
                    _query_param(
                        "apenas_ativas",
                        "Se 'true', retorna apenas estadias sem data de saída.",
                        enum=["true", "false"],
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de estadias retornada com sucesso.", "Estadia"
                        )
                    },
                    with_bad_request=True,
                ),
            }
        },
    },
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "openapi",
            "route": "/openapi.json",
            "rule_filter": lambda rule: not rule.endpoint.startswith("flasgger"),
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}


def init_swagger(app) -> Swagger:
    """Inicializa a UI do Swagger e a spec JSON da aplicação."""
    swagger = Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)
    app.extensions["swagger"] = swagger
    return swagger
