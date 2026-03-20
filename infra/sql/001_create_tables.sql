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
--   1. pessoa             (independente)
--   2. profissional       (depende de pessoa)
--   3. pessoa_rua         (independente)
--   4. consentimento      (depende de pessoa_rua)
--   5. prontuario         (depende de pessoa_rua + consentimento + profissional)
--   6. atendimento        (depende de pessoa_rua + profissional)
--   7. abrigo             (independente)
--   8. vaga_cama          (depende de abrigo)         ← substitui vaga
--   9. estadia            (depende de pessoa_rua + vaga_cama)
--  10. encaminhamento     (depende de atendimento)
--  11. historico_gestao   (depende de pessoa + abrigo)
--
-- Execute esse script UMA ÚNICA VEZ ao subir o ambiente pela primeira vez.
-- Se precisar recriar, use o script 002_drop_tables.sql antes.
-- =============================================================================

-- O banco de dados é definido pela variável MYSQL_DATABASE no .env.
-- Não é necessário 'USE' aqui — a conexão já aponta para o banco correto.

-- =============================================================================
-- TABELA: pessoa
-- Representa os USUÁRIOS do sistema (profissionais e gestores).
-- Diferente de `pessoa_rua`, esta tabela NÃO representa pessoas atendidas,
-- mas sim os operadores do sistema.
-- =============================================================================
CREATE TABLE IF NOT EXISTS pessoa (
    id_pessoa   INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(120)    NOT NULL,
    senha       VARCHAR(255)    NOT NULL
);
-- =============================================================================
-- TABELA: gestor
-- Representa os gestores responsáveis por gerirem os abrigos
-- que operam o sistema. Todo atendimento e encaminhamento precisa ter
-- um profissional responsável para manter rastreabilidade.
-- =============================================================================
CREATE TABLE IF NOT EXISTS gestor (
    id_gestor INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_pessoa INT UNSIGNED NOT NULL,
    instituicao VARCHAR(50),

    CONSTRAINT fk_gestor_pessoa FOREIGN KEY (id_pessoa) 
        REFERENCES pessoa(id_pessoa) ON DELETE CASCADE
);
-- =============================================================================
-- TABELA: profissional
-- Representa os assistentes sociais, educadores e demais profissionais
-- que operam o sistema. Todo atendimento precisa ter um profissional
-- responsável para manter rastreabilidade.
-- =============================================================================
CREATE TABLE IF NOT EXISTS profissional (
    id_profissional     INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    id_pessoa           INT UNSIGNED    NOT NULL,
    cargo               VARCHAR(100)    NOT NULL,
    registro_conselho   VARCHAR(50),

    CONSTRAINT fk_profissional_pessoa
        FOREIGN KEY (id_pessoa) REFERENCES pessoa(id_pessoa)
        ON DELETE CASCADE
);

-- =============================================================================
-- TABELA: pessoa_rua
-- NÚCLEO ABSOLUTO do sistema. Toda jornada começa aqui.
-- Aceita cadastro provisório SEM documentos (apenas apelido + descrição fisica).
-- Isso garante que nenhum atendimento seja bloqueado por burocracia (US01).
-- =============================================================================
CREATE TABLE IF NOT EXISTS pessoa_rua (
    id_pessoa_rua   INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    apelido         VARCHAR(100)    NOT NULL,
    descricao_fisica VARCHAR(255)   NOT NULL,
    nome_civil      VARCHAR(120),
    cpf_opcional    VARCHAR(11)     UNIQUE,
    nivel_risco     ENUM('baixo','medio','alto','critico') NOT NULL DEFAULT 'medio'
);

-- =============================================================================
-- TABELA: consentimento
-- Guardião legal do sistema, baseado na LGPD.
-- Funciona como CHAVE para desbloquear o prontuário social.
-- IMPORTANTE: a AUSÊNCIA de consentimento NUNCA bloqueia atendimentos.
-- Só bloqueia acesso ao prontuário (US02, US03).
-- =============================================================================
CREATE TABLE IF NOT EXISTS consentimento (
    id_pessoa_rua       INT UNSIGNED    PRIMARY KEY,
    ativo               BOOLEAN         NOT NULL DEFAULT TRUE,
    registrado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revogado_em         DATETIME,
    observacao          TEXT,

    CONSTRAINT fk_consentimento_pessoa
        FOREIGN KEY (id_pessoa_rua) REFERENCES pessoa_rua(id_pessoa_rua)
        ON DELETE RESTRICT
);

-- =============================================================================
-- TABELA: prontuario
-- Visão consolidada da trajetória social da pessoa.
-- SÓ PODE EXISTIR se houver consentimento válido (US02).
-- Se o consentimento for revogado, o prontuário fica READ-ONLY (US03).
-- A lógica de bloqueio é feita na camada de aplicação (Python), não aqui.
-- =============================================================================
CREATE TABLE IF NOT EXISTS prontuario (
    id_pessoa_rua INT UNSIGNED PRIMARY KEY,
    id_profissional INT UNSIGNED NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    resumo_historico TEXT,
    
    CONSTRAINT fk_prontuario_pessoa FOREIGN KEY (id_pessoa_rua)
        REFERENCES pessoa_rua(id_pessoa_rua) ON DELETE CASCADE,
    
    CONSTRAINT fk_prontuario_consentimento FOREIGN KEY (id_pessoa_rua)
        REFERENCES consentimento(id_pessoa_rua) ON DELETE RESTRICT,
    
    CONSTRAINT fk_prontuario_profissional FOREIGN KEY (id_profissional)
        REFERENCES profissional(id_profissional) ON DELETE RESTRICT
);

-- =============================================================================
-- TABELA: abrigo
-- Cadastro dos abrigos disponíveis na rede de apoio.
-- O campo `vagas_disponiveis` é gerenciado automaticamente pelo sistema
-- nos endpoints POST /vagas/entrada e PUT /vagas/:pessoa_id/saida (US07-US09).
-- =============================================================================
CREATE TABLE IF NOT EXISTS abrigo (
    id_abrigo           INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    nome                VARCHAR(150)    NOT NULL,
    endereco            VARCHAR(255)    NOT NULL,
    capacidade_total    INT UNSIGNED    NOT NULL,
    vagas_disponiveis   INT UNSIGNED    NOT NULL,
    telefone            VARCHAR(20),
    ativo               BOOLEAN         NOT NULL DEFAULT TRUE,
    criado_em           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_vagas CHECK (vagas_disponiveis <= capacidade_total)
);

-- =============================================================================
-- TABELA: atendimento
-- Registro operacional do dia a dia. O ÚNICO módulo que SEMPRE ocorre,
-- independente de consentimento ou prontuário.
-- Tipos: 'escuta', 'alimentacao', 'banho', 'saude', 'juridico', 'outro'
-- O atendimento_id é vínculo obrigatório para qualquer encaminhamento (US04).
-- =============================================================================
CREATE TABLE IF NOT EXISTS atendimento (
    id_atendimento      INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    id_pessoa_rua       INT UNSIGNED    NOT NULL,
    id_profissional     INT UNSIGNED    NOT NULL,
    id_abrigo           INT UNSIGNED    NOT NULL,
    tipo                ENUM('escuta','alimentacao','banho','saude','juridico','outro') NOT NULL,
    observacoes         TEXT,
    realizado_em        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_atendimento_pessoa
        FOREIGN KEY (id_pessoa_rua) REFERENCES pessoa_rua(id_pessoa_rua)
        ON DELETE RESTRICT,

    CONSTRAINT fk_atendimento_profissional
        FOREIGN KEY (id_profissional) REFERENCES profissional(id_profissional)
        ON DELETE RESTRICT,

    CONSTRAINT fk_atendimento_abrigo
        FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo)
        ON DELETE RESTRICT
);


-- =============================================================================
-- TABELA: vaga_cama
-- Inventário de camas numeradas por abrigo.
-- Populada automaticamente quando um abrigo é cadastrado via AbrigoModel.criar().
-- Cada cama tem número único dentro do seu abrigo e um status.
-- =============================================================================
CREATE TABLE IF NOT EXISTS vaga_cama (
    numero_cama_pk  INT UNSIGNED    NOT NULL,
    id_abrigo_fk    INT UNSIGNED    NOT NULL,
    status          ENUM('livre','ocupada') NOT NULL DEFAULT 'livre',

    PRIMARY KEY (numero_cama_pk, id_abrigo_fk),

    CONSTRAINT fk_vaga_cama_abrigo
        FOREIGN KEY (id_abrigo_fk) REFERENCES abrigo(id_abrigo)
        ON DELETE CASCADE
);


-- =============================================================================
-- TABELA: estadia
-- Registra a ocupação de uma cama específica por uma pessoa.
-- Substitui a tabela `vaga` — agora controlamos cama individual + motivo de saída.
-- Não requer prontuário, mas requer pessoa cadastrada (US08, US09).
-- =============================================================================
CREATE TABLE IF NOT EXISTS estadia (
    id_pessoa_rua_fk    INT UNSIGNED    NOT NULL,
    data_entrada_pk     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    numero_cama_fk      INT UNSIGNED    NOT NULL,
    id_abrigo_fk        INT UNSIGNED    NOT NULL,
    data_saida          DATETIME,
    motivo_saida        TEXT,

    PRIMARY KEY (id_pessoa_rua_fk, data_entrada_pk),

    CONSTRAINT fk_estadia_pessoa
        FOREIGN KEY (id_pessoa_rua_fk) REFERENCES pessoa_rua(id_pessoa_rua)
        ON DELETE RESTRICT,

    CONSTRAINT fk_estadia_vaga_cama
        FOREIGN KEY (numero_cama_fk, id_abrigo_fk) REFERENCES vaga_cama(numero_cama_pk, id_abrigo_fk)
        ON DELETE RESTRICT
);

-- =============================================================================
-- TABELA: encaminhamento
-- Formaliza a ponte entre o sistema e a rede externa (CRAS, CREAS, UBS, etc.).
-- =============================================================================
CREATE TABLE IF NOT EXISTS encaminhamento (
    id_encaminhamento_pk    INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    id_atendimento_fk       INT UNSIGNED    NOT NULL,
    orgaoDestino            VARCHAR(200)    NOT NULL,
    motivo                  TEXT            NOT NULL,
    prioridade              ENUM('baixa','media','alta') NOT NULL,
    status_acompanhamento   ENUM('pendente','atendido','resolvido','cancelado') NOT NULL DEFAULT 'pendente',

    CONSTRAINT fk_encaminhamento_atendimento
        FOREIGN KEY (id_atendimento_fk) REFERENCES atendimento(id_atendimento)
        ON DELETE RESTRICT
);

-- =============================================================================
-- TABELA: historico_gestao
-- Registra quem comandou qual abrigo e em qual período.
-- =============================================================================
CREATE TABLE IF NOT EXISTS historico_gestao (
    id_gestor       INT UNSIGNED    NOT NULL,
    id_abrigo       INT UNSIGNED    NOT NULL,
    data_inicio     DATETIME        NOT NULL,
    data_fim        DATETIME,

    PRIMARY KEY (id_gestor, id_abrigo, data_inicio),

    INDEX idx_hist_gestao_abrigo (id_abrigo),
    INDEX idx_hist_gestao_fim    (data_fim),

    CONSTRAINT fk_hist_gestao_gestor
        FOREIGN KEY (id_gestor) REFERENCES gestor(id_gestor)
        ON DELETE RESTRICT,

    CONSTRAINT fk_hist_gestao_abrigo
        FOREIGN KEY (id_abrigo) REFERENCES abrigo(id_abrigo)
        ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS atuacao
(
    id_profissional INT NOT NULL REFERENCES profissional(id_profissional),
    id_abrigo INT NOT NULL REFERENCES abrigo(id_abrigo),
    data_inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_fim DATETIME,

    PRIMARY KEY (id_profissional, id_abrigo)
);
