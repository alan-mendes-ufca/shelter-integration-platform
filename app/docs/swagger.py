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
            "description": "Fluxo de encaminhamentos formais e de emergência.",
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
                "id": {"type": "integer", "example": 7},
                "nome": {"type": "string", "example": "Maria Souza"},
                "cargo": {"type": "string", "example": "Assistente Social"},
                "email": {
                    "type": "string",
                    "format": "email",
                    "example": "maria@creas.gov.br",
                },
                "registro": {"type": "string", "example": "CRESS-SP 12345"},
            },
        },
        "ProfissionalCreateInput": {
            "type": "object",
            "required": ["nome", "cargo", "email"],
            "properties": {
                "nome": {"type": "string"},
                "cargo": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "registro": {"type": "string"},
            },
        },
        "Prontuario": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 11},
                "pessoa_id": {"type": "integer", "example": 42},
                "consentimento_id": {"type": "integer", "example": 8},
                "diagnostico_social": {
                    "type": "string",
                    "example": "Situação de alta vulnerabilidade.",
                },
                "observacoes": {
                    "type": "string",
                    "example": "Primeiro contato em abordagem social.",
                },
            },
        },
        "ProntuarioCreateInput": {
            "type": "object",
            "required": ["pessoa_id"],
            "properties": {
                "pessoa_id": {"type": "integer", "example": 42},
                "diagnostico_social": {"type": "string"},
                "observacoes": {"type": "string"},
            },
        },
        "ProntuarioUpdateInput": {
            "type": "object",
            "properties": {
                "diagnostico_social": {"type": "string"},
                "observacoes": {"type": "string"},
            },
        },
        "Abrigo": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 3},
                "nome": {"type": "string", "example": "Abrigo Esperança"},
                "endereco": {"type": "string", "example": "Rua das Flores, 100"},
                "capacidade_total": {"type": "integer", "example": 50},
                "vagas_disponiveis": {"type": "integer", "example": 12},
                "telefone": {"type": "string", "example": "(11) 9999-9999"},
            },
        },
        "AbrigoCreateInput": {
            "type": "object",
            "required": ["nome", "endereco", "capacidade_total"],
            "properties": {
                "nome": {"type": "string"},
                "endereco": {"type": "string"},
                "capacidade_total": {"type": "integer", "minimum": 1},
                "telefone": {"type": "string"},
            },
        },
        "Vaga": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 21},
                "pessoa_id": {"type": "integer", "example": 42},
                "abrigo_id": {"type": "integer", "example": 3},
                "status": {"type": "string", "example": "ocupada"},
                "entrada_em": {"type": "string", "example": "2026-03-05 18:10"},
                "saida_em": {"type": "string", "example": "2026-03-06 08:00"},
            },
        },
        "VagaEntradaInput": {
            "type": "object",
            "required": ["pessoa_id", "abrigo_id"],
            "properties": {
                "pessoa_id": {"type": "integer", "example": 42},
                "abrigo_id": {"type": "integer", "example": 3},
            },
        },
        "Encaminhamento": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 18},
                "atendimento_id": {"type": "integer", "example": 15},
                "prontuario_id": {"type": "integer", "example": 11},
                "tipo": {
                    "type": "string",
                    "enum": ["formal", "emergencia"],
                    "example": "formal",
                },
                "destino": {"type": "string", "example": "CRAS Vila Nova"},
                "motivo": {
                    "type": "string",
                    "example": "Necessita de benefício eventual.",
                },
                "status": {
                    "type": "string",
                    "enum": ["pendente", "atendido", "resolvido", "cancelado"],
                    "example": "pendente",
                },
                "cancelamento_motivo": {
                    "type": "string",
                    "example": "Duplicidade de emissão.",
                },
            },
        },
        "EncaminhamentoCreateInput": {
            "type": "object",
            "required": ["atendimento_id", "destino", "motivo"],
            "properties": {
                "atendimento_id": {"type": "integer", "example": 15},
                "destino": {"type": "string", "example": "CRAS Vila Nova"},
                "motivo": {
                    "type": "string",
                    "example": "Necessita de benefício eventual.",
                },
                "prontuario_id": {"type": "integer", "example": 11},
            },
        },
        "EncaminhamentoStatusInput": {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pendente", "atendido", "resolvido", "cancelado"],
                    "example": "atendido",
                },
                "cancelamento_motivo": {
                    "type": "string",
                    "example": "Encaminhamento emitido em duplicidade.",
                },
            },
        },
        "EncaminhamentoCancelamentoInput": {
            "type": "object",
            "required": ["motivo"],
            "properties": {
                "motivo": {
                    "type": "string",
                    "example": "Encaminhamento duplicado, gerado por engano.",
                }
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
                            "Lista de pessoas retornada com sucesso.",
                            "Usuario",
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
                "description": (
                    "Faz busca parcial para evitar cadastros duplicados. "
                    "Use o parâmetro de query obrigatório `apelido`."
                ),
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
                "description": (
                    "Atualiza parcialmente os campos da pessoa. "
                    "Campos aceitos: apelido, descricao_fisica, nome_civil e cpf_opcional. "
                    "Quando informado, `cpf_opcional` é validado antes da atualização."
                ),
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
                "description": (
                    "Permite filtrar por apelido, nome_civil, nivel_risco e "
                    "cpf_opcional (com ou sem máscara)."
                ),
                "parameters": [
                    _query_param(
                        "apelido",
                        "Filtro parcial por apelido.",
                        required=False,
                    ),
                    _query_param(
                        "nome_civil",
                        "Filtro parcial por nome civil.",
                        required=False,
                    ),
                    _query_param(
                        "nivel_risco",
                        "Filtro por nível de risco.",
                        required=False,
                        enum=["baixo", "medio", "alto", "critico"],
                    ),
                    _query_param(
                        "cpf_opcional",
                        "Filtro por CPF opcional (com ou sem máscara).",
                        required=False,
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
                        "409": _response("E-mail já cadastrado.", "ErrorResponse"),
                    },
                    with_bad_request=True,
                ),
            }
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
        "/prontuarios/{id}": {
            "get": {
                "tags": ["Prontuários"],
                "summary": "Retorna o prontuário integrado de uma pessoa.",
                "description": "Nesta operação, o parâmetro `id` representa o `pessoa_id`.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID da pessoa dona do prontuário.",
                    }
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Prontuário encontrado.", "Prontuario"),
                        "403": _response(
                            "Pessoa sem consentimento ativo.", "ErrorResponse"
                        ),
                        "404": _response("Prontuário não encontrado.", "ErrorResponse"),
                    }
                ),
            },
            "put": {
                "tags": ["Prontuários"],
                "summary": "Atualiza um prontuário existente.",
                "description": "Nesta operação, o parâmetro `id` representa o `prontuario_id`.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID do prontuário a atualizar.",
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
        "/abrigos": {
            "post": {
                "tags": ["Abrigos"],
                "summary": "Cadastra um abrigo no sistema.",
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
                        "Use `disponivel` para filtrar apenas abrigos com vagas livres.",
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
        "/vagas/entrada": {
            "post": {
                "tags": ["Vagas"],
                "summary": "Registra a entrada de uma pessoa em um abrigo.",
                "parameters": [
                    _body_param(
                        "VagaEntradaInput", "Pessoa e abrigo para o acolhimento."
                    )
                ],
                "responses": _default_responses(
                    success={
                        "201": _response("Entrada registrada com sucesso.", "Vaga"),
                        "409": _response(
                            "Sem vagas disponíveis ou pessoa já acolhida.",
                            "ErrorResponse",
                        ),
                    },
                    with_bad_request=True,
                ),
            }
        },
        "/vagas/{vaga_id}/saida": {
            "put": {
                "tags": ["Vagas"],
                "summary": "Registra a saída de uma pessoa do abrigo.",
                "parameters": [
                    _path_param("vaga_id", "ID do registro de ocupação da vaga.")
                ],
                "responses": _default_responses(
                    success={
                        "200": _response("Saída registrada com sucesso.", "Vaga"),
                        "404": _response("Vaga não encontrada.", "ErrorResponse"),
                        "409": _response(
                            "Saída já registrada para essa vaga.", "ErrorResponse"
                        ),
                    }
                ),
            }
        },
        "/encaminhamentos": {
            "post": {
                "tags": ["Encaminhamentos"],
                "summary": "Cria um encaminhamento vinculado a um atendimento.",
                "description": "O tipo é determinado automaticamente: `formal` com prontuário, `emergencia` sem prontuário.",
                "parameters": [
                    _body_param(
                        "EncaminhamentoCreateInput", "Dados mínimos do encaminhamento."
                    )
                ],
                "responses": _default_responses(
                    success={
                        "201": _response(
                            "Encaminhamento criado com sucesso.", "Encaminhamento"
                        )
                    },
                    with_bad_request=True,
                ),
            },
            "get": {
                "tags": ["Encaminhamentos"],
                "summary": "Filtra encaminhamentos por status.",
                "parameters": [
                    _query_param(
                        "status",
                        "Status do encaminhamento.",
                        required=True,
                        enum=["pendente", "atendido", "resolvido", "cancelado"],
                    )
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de encaminhamentos filtrados por status.",
                            "Encaminhamento",
                        )
                    },
                    with_bad_request=True,
                ),
            },
        },
        "/encaminhamentos/{id}": {
            "get": {
                "tags": ["Encaminhamentos"],
                "summary": "Lista encaminhamentos de uma pessoa.",
                "description": "Nesta operação, o parâmetro `id` representa o `pessoa_id`.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID da pessoa consultada.",
                    }
                ],
                "responses": _default_responses(
                    success={
                        "200": _array_response(
                            "Lista de encaminhamentos retornada com sucesso.",
                            "Encaminhamento",
                        )
                    }
                ),
            },
            "delete": {
                "tags": ["Encaminhamentos"],
                "summary": "Cancela um encaminhamento.",
                "description": "Nesta operação, o parâmetro `id` representa o `encaminhamento_id`.",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": "ID do encaminhamento a cancelar.",
                    },
                    _body_param(
                        "EncaminhamentoCancelamentoInput",
                        "Motivo obrigatório do cancelamento.",
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response(
                            "Encaminhamento cancelado com sucesso.", "Encaminhamento"
                        ),
                        "404": _response(
                            "Encaminhamento não encontrado.", "ErrorResponse"
                        ),
                        "409": _response(
                            "Encaminhamento não pode mais ser cancelado.",
                            "ErrorResponse",
                        ),
                    },
                    with_bad_request=True,
                ),
            },
        },
        "/encaminhamentos/{encaminhamento_id}/status": {
            "put": {
                "tags": ["Encaminhamentos"],
                "summary": "Atualiza o status de um encaminhamento.",
                "parameters": [
                    _path_param(
                        "encaminhamento_id", "ID do encaminhamento a atualizar."
                    ),
                    _body_param(
                        "EncaminhamentoStatusInput",
                        "Novo status e motivo de cancelamento, quando aplicável.",
                    ),
                ],
                "responses": _default_responses(
                    success={
                        "200": _response(
                            "Status atualizado com sucesso.", "Encaminhamento"
                        ),
                        "404": _response(
                            "Encaminhamento não encontrado.", "ErrorResponse"
                        ),
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
