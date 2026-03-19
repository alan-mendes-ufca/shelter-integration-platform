-- =============================================================================
-- MIGRATION 002 — Drop de todas as tabelas (USE APENAS EM DESENVOLVIMENTO)
-- =============================================================================
--
-- Estagiário, ATENÇÃO MÁXIMA:
-- Esse arquivo serve para destruir e recriar o banco do zero durante o dev.
-- JAMAIS rode isso em produção.
--
-- A ordem de DROP é o inverso da criação, respeitando as foreign keys.
-- Se tentar dropar uma tabela "pai" antes das "filhas", o MySQL rejeita.
--
-- Uso correto:
--   mysql -u root -p atendimento_db < 002_drop_tables.sql
--   mysql -u root -p atendimento_db < 001_create_tables.sql
-- =============================================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS encaminhamento;
DROP TABLE IF EXISTS estadia;       -- substitui vaga
DROP TABLE IF EXISTS vaga_cama;     -- substitui vaga
DROP TABLE IF EXISTS atuacao;
DROP TABLE IF EXISTS abrigo;
DROP TABLE IF EXISTS atendimento;
DROP TABLE IF EXISTS prontuario;
DROP TABLE IF EXISTS consentimento;
DROP TABLE IF EXISTS pessoa_rua;
DROP TABLE IF EXISTS profissional;
DROP TABLE IF EXISTS historico_gestao;
DROP TABLE IF EXISTS pessoa;

SET FOREIGN_KEY_CHECKS = 1;
