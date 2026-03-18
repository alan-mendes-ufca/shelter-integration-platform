-- =============================================================================
-- MIGRATION 003 — Seed de dados para desenvolvimento e testes manuais
-- =============================================================================
--
-- Este arquivo popula as tabelas com tuplas iniciais para facilitar:
-- - testes exploratórios de endpoints;
-- - validação de integrações;
-- - demonstração local da API.
--
-- IMPORTANTE:
-- - IDs são definidos explicitamente para manter referências previsíveis.
-- - Deve ser executado APÓS 001_create_tables.sql.
-- =============================================================================

-- Pessoa (usuários do sistema)
INSERT INTO pessoa (id_pessoa, nome, senha)
VALUES
    (1, 'Gestor Demo', 'senha123'),
    (2, 'Assistente Social Demo', 'senha123');

-- Profissional
INSERT INTO profissional (id_profissional, id_pessoa, cargo, registro_conselho)
VALUES
    (1, 2, 'assistente_social', 'CRESS-1001');

-- Pessoas em situação de rua
INSERT INTO pessoa_rua (
    id_pessoa_rua,
    apelido,
    descricao_fisica,
    nome_civil,
    cpf_opcional,
    nivel_risco
)
VALUES
    (1, 'Joao da Praca', 'Homem, 45 anos, mochila azul', 'Joao Silva', '39053344705', 'alto'),
    (2, 'Maria Centro', 'Mulher, 38 anos, casaco vermelho', NULL, NULL, 'medio');

-- Consentimento
INSERT INTO consentimento (
    id_consentimento,
    id_pessoa_rua,
    ativo,
    registrado_em,
    revogado_em,
    observacao
)
VALUES
    (1, 1, TRUE, CURRENT_TIMESTAMP, NULL, 'Consentimento ativo para uso de dados.'),
    (2, 2, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Consentimento revogado a pedido da pessoa.');

-- Prontuário
INSERT INTO prontuario (
    id_prontuario,
    id_pessoa_rua,
    id_consentimento,
    id_profissional,
    data_criacao,
    resumo_historico
)
VALUES
    (1, 1, 1, 1, CURRENT_TIMESTAMP, 'Pessoa acompanhada em atendimentos recorrentes.');

-- Abrigos
INSERT INTO abrigo (
    id_abrigo,
    nome,
    endereco,
    capacidade_total,
    vagas_disponiveis,
    telefone,
    ativo,
    criado_em
)
VALUES
    (1, 'Abrigo Esperanca', 'Rua das Flores, 100', 50, 49, '(11) 99999-1111', TRUE, CURRENT_TIMESTAMP),
    (2, 'Abrigo Nova Vida', 'Av. Central, 250', 30, 30, '(11) 99999-2222', TRUE, CURRENT_TIMESTAMP);

-- Atendimento
INSERT INTO atendimento (
    id_atendimento,
    id_pessoa_rua,
    id_profissional,
    id_abrigo,
    tipo,
    observacoes,
    realizado_em,
    atualizado_em
)
VALUES
    (1, 1, 1, 1, 'escuta', 'Acolhimento inicial e escuta qualificada.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (2, 1, 1, 1, 'alimentacao', 'Encaminhada para refeicao no abrigo.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Vaga
INSERT INTO vaga (
    id_vaga,
    id_pessoa_rua,
    abrigo_id,
    status,
    entrada_em,
    saida_em
)
VALUES
    (1, 1, 1, 'ocupada', CURRENT_TIMESTAMP, NULL);

-- Encaminhamento
INSERT INTO encaminhamento (
    id_encaminhamento_pk,
    id_atendimento_fk,
    orgaoDestino,
    motivo,
    prioridade,
    status_acompanhamento
)
VALUES
    (1, 1, 'CRAS Centro', 'Solicitacao de beneficio eventual.', 'media', 'pendente');

-- Historico de gestao
INSERT INTO historico_gestao (
    id_gestor_fk,
    id_abrigo_fk,
    data_inicio_pk,
    data_fim
)
VALUES
    (1, 1, CURRENT_TIMESTAMP, NULL);

-- Atuacao
INSERT INTO atuacao (
    id_profissional,
    id_abrigo,
    data_inicio,
    data_fim
)
VALUES
    (1, 1, CURRENT_TIMESTAMP, NULL);
