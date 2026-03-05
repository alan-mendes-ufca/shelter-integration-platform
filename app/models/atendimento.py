"""
Model: Atendimento
==================

Estagiário, esse é o model do módulo mais simples e ao mesmo tempo mais
importante operacionalmente: o registro de atendimentos.

Por que é o mais simples? Porque não tem restrições complexas de consentimento.
Por que é o mais importante? Porque é a base de tudo — todo encaminhamento
obrigatoriamente tem um atendimento_id associado.

Guarda bem essa frase: "Sem atendimento, não há encaminhamento."
                        "Sem cadastro da pessoa, não há atendimento."
"""

from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class AtendimentoModel:
    """
    Gerencia o registro de atendimentos diários (escuta, banho, alimentação, etc.).

    Esse model nunca deve verificar consentimento — isso é responsabilidade
    do controller de Prontuário quando for consolidar as informações.
    Aqui, a regra é simples: se a pessoa existe, o atendimento pode ser criado.
    """

    @staticmethod
    def criar(dados: dict) -> dict | None:
        """
        Registra um novo atendimento no sistema (US04).

        Sempre possível, independente de consentimento ou prontuário.

        Args:
            dados (dict): Dados do atendimento.
                          Obrigatórios: 'pessoa_id', 'profissional_id', 'tipo', 'unidade'
                          Opcionais: 'observacoes', 'realizado_em'

        Returns:
            dict | None: Atendimento recém-criado.

        TODO (estagiário): Implemente o INSERT em `atendimento`.
                           O campo `tipo` deve ser um dos valores do ENUM no banco:
                           'escuta', 'alimentacao', 'banho', 'saude', 'juridico', 'outro'.
                           Valide isso no controller antes de chamar esse método.
        """
        # TODO: Implementar
        raise NotImplementedError("AtendimentoModel.criar() ainda não foi implementado.")

    @staticmethod
    def listar_por_pessoa(pessoa_id: int) -> list[dict]:
        """
        Lista todos os atendimentos de uma pessoa em ordem cronológica (US05).

        Esse resultado é a base do histórico exibido no prontuário integrado,
        quando o consentimento está ativo.

        Args:
            pessoa_id (int): ID da pessoa.

        Returns:
            list[dict]: Lista de atendimentos ordenados por `realizado_em` DESC.

        TODO (estagiário): SELECT at.*, p.nome AS profissional_nome
                           FROM atendimento at
                           JOIN profissional p ON at.profissional_id = p.id
                           WHERE at.pessoa_id = %s
                           ORDER BY at.realizado_em DESC
                           Tente fazer o JOIN para já trazer o nome do profissional.
                           Isso evita N+1 queries no controller.
        """
        # TODO: Implementar
        raise NotImplementedError("AtendimentoModel.listar_por_pessoa() ainda não foi implementado.")

    @staticmethod
    def listar_por_unidade_e_periodo(unidade: str, data_inicio: str, data_fim: str) -> list[dict]:
        """
        Retorna atendimentos filtrados por unidade e período de datas.

        Usado para gerar estatísticas e relatórios operacionais da unidade.

        Args:
            unidade (str): Nome ou parte do nome da unidade.
            data_inicio (str): Data inicial no formato 'YYYY-MM-DD'.
            data_fim (str): Data final no formato 'YYYY-MM-DD'.

        Returns:
            list[dict]: Lista de atendimentos no período.

        TODO (estagiário): Use BETWEEN para o período de datas.
                           Exemplo: WHERE unidade LIKE %s AND realizado_em BETWEEN %s AND %s
                           Lembra: o %s do LIKE deve receber f'%{unidade}%' como valor,
                           não coloque o % dentro do placeholder.
        """
        # TODO: Implementar
        raise NotImplementedError("AtendimentoModel.listar_por_unidade_e_periodo() ainda não foi implementado.")

    @staticmethod
    def atualizar(atendimento_id: int, dados: dict) -> dict | None:
        """
        Corrige dados de um atendimento registrado com erro.

        Toda alteração deve ter um log de auditoria — o campo `atualizado_em`
        é atualizado automaticamente pelo banco via ON UPDATE CURRENT_TIMESTAMP.

        Args:
            atendimento_id (int): ID do atendimento a corrigir.
            dados (dict): Campos a atualizar.

        Returns:
            dict | None: Atendimento atualizado ou None se não encontrado.

        TODO (estagiário): Implemente UPDATE + SELECT de retorno.
                           No futuro, considere criar uma tabela de `audit_log`
                           para registrar quem alterou o quê e quando.
        """
        # TODO: Implementar
        raise NotImplementedError("AtendimentoModel.atualizar() ainda não foi implementado.")

    @staticmethod
    def deletar(atendimento_id: int) -> bool:
        """
        Remove um atendimento registrado indevidamente.

        ATENÇÃO: Só deve ser chamado após verificação de permissão de gestor
        no controller. Nunca exponha esse método sem autenticação.

        Args:
            atendimento_id (int): ID do atendimento a remover.

        Returns:
            bool: True se deletado com sucesso, False se não encontrado.

        TODO (estagiário): DELETE FROM atendimento WHERE id = %s.
                           Use cursor.rowcount para saber se alguma linha foi afetada.
                           rowcount == 0 → não encontrado → controller retorna 404.
                           rowcount == 1 → sucesso → controller retorna 204 No Content.
        """
        # TODO: Implementar
        raise NotImplementedError("AtendimentoModel.deletar() ainda não foi implementado.")


