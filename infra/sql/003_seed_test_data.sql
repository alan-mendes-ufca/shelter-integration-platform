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
    (2, 'Assistente Social Demo', 'senha123'),
    (3, 'Educador Demo', 'senha123'),
    (4, 'Enfermeira Demo', 'senha123'),
    (5, 'Psicologa Demo', 'senha123'),
    (6, 'Assistente Noturno Demo', 'senha123');

-- Profissional
INSERT INTO profissional (id_profissional, id_pessoa, cargo, registro_conselho)
VALUES
    (1, 2, 'assistente_social', 'CRESS-1001'),
    (2, 3, 'educador_social', 'REG-2002'),
    (3, 4, 'enfermeira', 'COREN-3003'),
    (4, 5, 'psicologa', 'CRP-4004'),
    (5, 6, 'assistente_social', 'CRESS-5005');

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
    (2, 'Maria Centro', 'Mulher, 38 anos, casaco vermelho', NULL, NULL, 'medio'),
    (3, 'Carlos Ponte', 'Homem, 52 anos, barba grisalha', 'Carlos Mendes', '81424606020', 'alto'),
    (4, 'Lia Terminal', 'Mulher, 29 anos, mochila verde', NULL, NULL, 'baixo'),
    (5, 'Pedro Mercado', 'Homem, 33 anos, jaqueta preta', 'Pedro Costa', '11144477735', 'medio'),
    (6, 'Ana Lagoa', 'Mulher, 41 anos, cabelo curto', 'Ana Paula Rocha', '98765432100', 'critico');

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
    (2, 2, FALSE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Consentimento revogado a pedido da pessoa.'),
    (3, 1, FALSE, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 30 DAY), DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 7 DAY), 'Consentimento anterior revogado para atualizacao.'),
    (4, 3, TRUE, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 10 DAY), NULL, 'Consentimento ativo apos acolhimento.'),
    (5, 4, FALSE, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 4 DAY), DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), 'Revogado por solicitacao da pessoa.'),
    (6, 5, TRUE, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), NULL, 'Consentimento ativo para acompanhamento psicossocial.');

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
    (1, 1, 1, 1, CURRENT_TIMESTAMP, 'Pessoa acompanhada em atendimentos recorrentes.'),
    (2, 3, 4, 2, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 9 DAY), 'Historico de acolhimento com foco em reinsercao social.'),
    (3, 5, 6, 4, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), 'Acompanhamento psicossocial em andamento.');

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
    (2, 'Abrigo Nova Vida', 'Av. Central, 250', 30, 29, '(11) 99999-2222', TRUE, CURRENT_TIMESTAMP),
    (3, 'Abrigo Bom Caminho', 'Rua da Integracao, 80', 20, 19, '(11) 99999-3333', TRUE, CURRENT_TIMESTAMP);

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
    (2, 1, 1, 1, 'alimentacao', 'Encaminhada para refeicao no abrigo.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    (3, 3, 2, 2, 'banho', 'Acesso ao banho e kit higiene.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 8 DAY), DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 8 DAY)),
    (4, 4, 3, 2, 'saude', 'Encaminhada para avaliacao de enfermagem.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY), DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY)),
    (5, 5, 4, 3, 'escuta', 'Escuta com foco em vinculo familiar.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY)),
    (6, 6, 5, 3, 'juridico', 'Orientacoes sobre documentacao civil.', DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY));

-- Vaga Cama
INSERT INTO vaga_cama (
    numero_cama_pk,
    id_abrigo_fk,
    status
)
VALUES
    (1, 1, 'ocupada'),
    (2, 1, 'livre'),
    (3, 1, 'livre'),
    (1, 2, 'ocupada'),
    (2, 2, 'livre'),
    (3, 2, 'livre'),
    (1, 3, 'ocupada'),
    (2, 3, 'livre'),
    (3, 3, 'livre');

-- Estadia
INSERT INTO estadia (
    id_pessoa_rua_fk,
    data_entrada_pk,
    numero_cama_fk,
    id_abrigo_fk,
    data_saida,
    motivo_saida
)
VALUES
    (1, CURRENT_TIMESTAMP, 1, 1, NULL, NULL),
    (3, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 8 DAY), 1, 2, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 6 DAY), 'Transferencia para abrigo com rede familiar.'),
    (4, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 3 DAY), 1, 2, NULL, NULL),
    (6, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY), 1, 3, NULL, NULL);

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
    (1, 1, 'CRAS Centro', 'Solicitacao de beneficio eventual.', 'media', 'pendente'),
    (2, 3, 'UBS Central', 'Avaliacao clinica inicial.', 'alta', 'atendido'),
    (3, 4, 'CAPS', 'Acompanhamento em saude mental.', 'alta', 'pendente'),
    (4, 5, 'CREAS Norte', 'Apoio para reintegracao familiar.', 'media', 'resolvido');

-- Historico de gestao
INSERT INTO historico_gestao (
    id_gestor_fk,
    id_abrigo_fk,
    data_inicio_pk,
    data_fim
)
VALUES
    (1, 1, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 60 DAY), NULL),
    (1, 2, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 45 DAY), NULL),
    (1, 3, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 20 DAY), NULL);

-- Atuacao
INSERT INTO atuacao (
    id_profissional,
    id_abrigo,
    data_inicio,
    data_fim
)
VALUES
    (1, 1, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 60 DAY), NULL),
    (2, 2, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 30 DAY), NULL),
    (3, 2, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 15 DAY), NULL),
    (4, 3, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 5 DAY), NULL),
    (5, 3, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY), NULL);
