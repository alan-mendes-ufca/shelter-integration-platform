"""
Model: Profissional
===================

Estagiário, esse model é simples mas fundamental para rastreabilidade.

Todo atendimento, todo encaminhamento precisa ter um `profissional_id` associado.
Isso garante que qualquer ação no sistema possa ser auditada:
"Quem fez isso? Quando? Em qual unidade?"

Por enquanto não implementamos autenticação JWT (isso vem depois),
mas já estamos estruturando o sistema para suportá-la.
"""

from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class ProfissionalModel:
    """
    Gerencia o cadastro de profissionais que operam o sistema.

    Profissionais são: assistentes sociais, educadores sociais,
    psicólogos, coordenadores, etc.
    """

    @staticmethod
    def criar(dados: dict) -> dict | None:
        """
        Cadastra um novo profissional no sistema.

        Args:
            dados (dict): Dados do profissional.
                          Obrigatórios: 'nome', 'cargo', 'email'
                          Opcionais: 'registro' (ex: CRESS-12345)

        Returns:
            dict | None: Profissional recém-criado.

        TODO (estagiário): INSERT INTO profissional (...) VALUES (...).
                           O campo `email` tem UNIQUE constraint no banco.
                           Se tentar cadastrar email duplicado, o MySQL vai lançar
                           um erro de constraint. Trate isso no controller
                           retornando HTTP 409 Conflict com mensagem amigável.
        """
        # TODO: Implementar
        raise NotImplementedError("ProfissionalModel.criar() ainda não foi implementado.")

    @staticmethod
    def buscar_por_id(profissional_id: int) -> dict | None:
        """
        Retorna os dados de um profissional pelo ID.

        Args:
            profissional_id (int): ID do profissional.

        Returns:
            dict | None: Dados do profissional ou None se não existir.

        TODO (estagiário): SELECT * FROM profissional WHERE id = %s AND ativo = TRUE.
                           Note o filtro `ativo = TRUE` — profissionais desativados
                           não devem aparecer normalmente no sistema.
        """
        # TODO: Implementar
        raise NotImplementedError("ProfissionalModel.buscar_por_id() ainda não foi implementado.")


