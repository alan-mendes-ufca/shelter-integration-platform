-- =============================================================================
-- MIGRATION 002 — Drop de todas as tabelas (USE APENAS EM DESENVOLVIMENTO)
-- =============================================================================
--
-- Estagiário, ATENÇÃO MÁXIMA:
--
-- Esse arquivo serve para destruir e recriar o banco do zero durante o dev.
-- JAMAIS rode isso em produção. Sério. Jamais.
--
-- A ordem de DROP é o inverso da criação, respeitando as foreign keys.
-- Se tentar dropar uma tabela "pai" antes das "filhas" que a referenciam,
-- o MySQL vai rejeitar com erro de constraint.
--
-- Uso correto:
--   mysql -u root -p atendimento_db < 002_drop_tables.sql
--   mysql -u root -p atendimento_db < 001_create_tables.sql
-- =============================================================================

-- O banco de dados é definido pela variável MYSQL_DATABASE no .env.

-- Desativa checagem de FK temporariamente para facilitar o drop em massa
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS estadia;
DROP TABLE IF EXISTS encaminhamento;
DROP TABLE IF EXISTS vaga;
DROP TABLE IF EXISTS abrigo;
DROP TABLE IF EXISTS atendimento;
DROP TABLE IF EXISTS prontuario;
DROP TABLE IF EXISTS consentimento;
DROP TABLE IF EXISTS pessoa_rua;
DROP TABLE IF EXISTS profissional;
DROP TABLE IF EXISTS historico_gestao;

-- Reativa checagem de FK
SET FOREIGN_KEY_CHECKS = 1;
