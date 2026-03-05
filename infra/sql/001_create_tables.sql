-- =============================================================================
-- MIGRATION 001 — Criação das tabelas principais do sistema de atendimento
-- =============================================================================
--
-- Estagiário, presta atenção aqui:
--
-- Esse arquivo é a base de TUDO. Cada tabela aqui vai virar um Model em Python,
-- cada coluna vai virar um campo validado no endpoint. Então lê com calma.
--
-- A ordem de criação importa muito por causa das FOREIGN KEYS.
-- Nunca tente criar uma tabela que referencia outra que ainda não existe.
-- A ordem correta é:
--   1. profissional       (independente)
--   2. pessoa_rua         (independente)
--   3. consentimento      (depende de pessoa_rua)
--   4. prontuario         (depende de pessoa_rua + consentimento)
--   5. atendimento        (depende de pessoa_rua + profissional)
--   6. abrigo             (independente)
--   7. vaga               (depende de pessoa_rua + abrigo)
--   8. encaminhamento     (depende de atendimento + prontuario)
--
-- Execute esse script UMA ÚNICA VEZ ao subir o ambiente pela primeira vez.
-- Se precisar recriar, use o script 002_drop_tables.sql antes.
-- =============================================================================

-- Garante que estamos usando o banco correto
-- (o nome do banco vem da variável de ambiente MYSQL_DATABASE no .env)
USE atendimento_db;

-- =============================================================================
-- TABELA: profissional
-- Representa os assistentes sociais, educadores e demais profissionais
-- que operam o sistema. Todo atendimento e encaminhamento precisa ter
-- um profissional responsável para manter rastreabilidade.
-- =============================================================================
CREATE TABLE IF NOT EXISTS profissional (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(150)    NOT NULL,
    registro        VARCHAR(50)     UNIQUE,         -- Ex: CRESS-12345 (pode ser nulo em cadastros provisórios)
    cargo           VARCHAR(100)    NOT NULL,        -- Ex: "Assistente Social", "Educador Social"
    email           VARCHAR(150)    UNIQUE NOT NULL,
    ativo           BOOLEAN         NOT NULL DEFAULT TRUE,
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABELA: pessoa_rua
-- NÚCLEO ABSOLUTO do sistema. Toda jornada começa aqui.
-- Aceita cadastro provisório SEM documentos (apenas apelido + aparência).
-- Isso garante que nenhum atendimento seja bloqueado por burocracia (US01).
-- =============================================================================
CREATE TABLE IF NOT EXISTS pessoa_rua (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    apelido         VARCHAR(100)    NOT NULL,                -- Campo obrigatório mesmo sem documentos
    nome_real       VARCHAR(150),                            -- Preenchido quando/se a pessoa informar
    cpf             VARCHAR(14)     UNIQUE,                  -- UNIQUE mas nullable para cadastros provisórios
    data_nascimento DATE,
    genero          VARCHAR(50),
    aparencia       TEXT            NOT NULL,                -- Descrição física para identificação sem documentos
    endereco_ref    VARCHAR(255),                            -- Ponto de referência onde costuma ficar
    nivel_risco     ENUM('baixo','medio','alto','critico') NOT NULL DEFAULT 'baixo',  -- Alimenta US06
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABELA: consentimento
-- Guardião legal do sistema, baseado na LGPD.
-- Funciona como CHAVE para desbloquear o prontuário social.
-- IMPORTANTE: a AUSÊNCIA de consentimento NUNCA bloqueia atendimentos.
-- Só bloqueia acesso ao prontuário (US02, US03).
-- =============================================================================
CREATE TABLE IF NOT EXISTS consentimento (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    pessoa_id       INT UNSIGNED    NOT NULL,
    ativo           BOOLEAN         NOT NULL DEFAULT TRUE,   -- FALSE = revogado
    registrado_em   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revogado_em     DATETIME,                                -- Preenchido quando/se revogado (US03)
    observacao      TEXT,                                    -- Contexto do consentimento ou revogação

    CONSTRAINT fk_consentimento_pessoa
        FOREIGN KEY (pessoa_id) REFERENCES pessoa_rua(id)
        ON DELETE RESTRICT                                   -- Não permite deletar pessoa com consentimento
);

-- =============================================================================
-- TABELA: prontuario
-- Visão consolidada da trajetória social da pessoa.
-- SÓ PODE EXISTIR se houver consentimento válido (US02).
-- Se o consentimento for revogado, o prontuário fica READ-ONLY (US03).
-- A lógica de bloqueio é feita na camada de aplicação (Python), não aqui.
-- =============================================================================
CREATE TABLE IF NOT EXISTS prontuario (
    id                  INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    pessoa_id           INT UNSIGNED    NOT NULL UNIQUE,     -- 1 prontuário por pessoa
    consentimento_id    INT UNSIGNED    NOT NULL,
    diagnostico_social  TEXT,                                -- Síntese feita pelo assistente social
    observacoes         TEXT,
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_prontuario_pessoa
        FOREIGN KEY (pessoa_id) REFERENCES pessoa_rua(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_prontuario_consentimento
        FOREIGN KEY (consentimento_id) REFERENCES consentimento(id)
        ON DELETE RESTRICT
);

-- =============================================================================
-- TABELA: atendimento
-- Registro operacional do dia a dia. O ÚNICO módulo que SEMPRE ocorre,
-- independente de consentimento ou prontuário.
-- Tipos: 'escuta', 'alimentacao', 'banho', 'saude', 'juridico', 'outro'
-- O atendimento_id é vínculo obrigatório para qualquer encaminhamento (US04).
-- =============================================================================
CREATE TABLE IF NOT EXISTS atendimento (
    id                  INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    pessoa_id           INT UNSIGNED    NOT NULL,
    profissional_id     INT UNSIGNED    NOT NULL,
    tipo                ENUM('escuta','alimentacao','banho','saude','juridico','outro') NOT NULL,
    unidade             VARCHAR(150)    NOT NULL,            -- Nome/localização da unidade de atendimento
    observacoes         TEXT,
    realizado_em        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_atendimento_pessoa
        FOREIGN KEY (pessoa_id) REFERENCES pessoa_rua(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_atendimento_profissional
        FOREIGN KEY (profissional_id) REFERENCES profissional(id)
        ON DELETE RESTRICT
);

-- =============================================================================
-- TABELA: abrigo
-- Cadastro dos abrigos disponíveis na rede de apoio.
-- O campo `vagas_disponiveis` é gerenciado automaticamente pelo sistema
-- nos endpoints POST /vagas/entrada e PUT /vagas/:id/saida (US07, US08, US09).
-- =============================================================================
CREATE TABLE IF NOT EXISTS abrigo (
    id                  INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    nome                VARCHAR(150)    NOT NULL,
    endereco            VARCHAR(255)    NOT NULL,
    capacidade_total    INT UNSIGNED    NOT NULL,
    vagas_disponiveis   INT UNSIGNED    NOT NULL,           -- Decrementado/incrementado automaticamente
    telefone            VARCHAR(20),
    ativo               BOOLEAN         NOT NULL DEFAULT TRUE,
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Garante que vagas_disponiveis nunca ultrapasse a capacidade
    CONSTRAINT chk_vagas CHECK (vagas_disponiveis <= capacidade_total)
);

-- =============================================================================
-- TABELA: vaga
-- Registra a ocupação de vagas em abrigos.
-- Uma vaga pertence a UMA pessoa e UM abrigo.
-- Status: 'ocupada' ou 'liberada'.
-- Não requer prontuário, mas requer pessoa cadastrada (US08, US09).
-- =============================================================================
CREATE TABLE IF NOT EXISTS vaga (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    pessoa_id       INT UNSIGNED    NOT NULL,
    abrigo_id       INT UNSIGNED    NOT NULL,
    status          ENUM('ocupada','liberada') NOT NULL DEFAULT 'ocupada',
    entrada_em      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    saida_em        DATETIME,                               -- Preenchido no PUT /vagas/:id/saida

    CONSTRAINT fk_vaga_pessoa
        FOREIGN KEY (pessoa_id) REFERENCES pessoa_rua(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_vaga_abrigo
        FOREIGN KEY (abrigo_id) REFERENCES abrigo(id)
        ON DELETE RESTRICT
);

-- =============================================================================
-- TABELA: encaminhamento
-- Formaliza a ponte entre o sistema e a rede externa (CRAS, CREAS, UBS, etc.).
-- Dois tipos:
--   - FORMAL:     prontuario_id preenchido → dados completos
--   - EMERGÊNCIA: prontuario_id NULL → sem consentimento, dados mínimos
-- Sempre exige um atendimento registrado (US10).
-- =============================================================================
CREATE TABLE IF NOT EXISTS encaminhamento (
    id                  INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    atendimento_id      INT UNSIGNED    NOT NULL,            -- OBRIGATÓRIO em qualquer tipo
    prontuario_id       INT UNSIGNED,                        -- NULL = encaminhamento de emergência
    destino             VARCHAR(200)    NOT NULL,            -- Ex: "CRAS Vila Nova", "UBS Centro"
    motivo              TEXT            NOT NULL,
    status              ENUM('pendente','atendido','resolvido','cancelado') NOT NULL DEFAULT 'pendente',
    tipo                ENUM('formal','emergencia') NOT NULL, -- Derivado de prontuario_id, mas salvo explicitamente
    cancelamento_motivo TEXT,                                -- Preenchido apenas se status = 'cancelado'
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_encaminhamento_atendimento
        FOREIGN KEY (atendimento_id) REFERENCES atendimento(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_encaminhamento_prontuario
        FOREIGN KEY (prontuario_id) REFERENCES prontuario(id)
        ON DELETE RESTRICT                                   -- NULL é permitido (ON DELETE RESTRICT só age se não for NULL)
);

-- =============================================================================
-- ÍNDICES DE PERFORMANCE
-- Estagiário: índices aceleram buscas frequentes. Coloque-os nas colunas
-- que aparecem em WHERE, JOIN ou ORDER BY com frequência.
-- =============================================================================
CREATE INDEX idx_pessoa_apelido        ON pessoa_rua(apelido);
CREATE INDEX idx_pessoa_cpf            ON pessoa_rua(cpf);
CREATE INDEX idx_consentimento_pessoa  ON consentimento(pessoa_id);
CREATE INDEX idx_atendimento_pessoa    ON atendimento(pessoa_id);
CREATE INDEX idx_atendimento_unidade   ON atendimento(unidade);
CREATE INDEX idx_atendimento_data      ON atendimento(realizado_em);
CREATE INDEX idx_encaminhamento_status ON encaminhamento(status);
CREATE INDEX idx_vaga_status           ON vaga(status);

