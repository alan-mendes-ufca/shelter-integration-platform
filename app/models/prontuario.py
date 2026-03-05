"""
Model: Prontuario
=================

Estagiário, esse é o model mais complexo do sistema. Presta bem atenção.

O prontuário não é apenas uma tabela — ele é uma VISÃO CONSOLIDADA que agrega
dados de múltiplas tabelas via JOINs. Quando o controller pedir o prontuário
completo de uma pessoa, esse model vai executar uma query com vários JOINs
e retornar tudo de uma vez.

Regras de negócio CRÍTICAS que você nunca pode esquecer:
1. Prontuário SÓ pode ser CRIADO se houver consentimento ativo (verifique antes).
2. Prontuário SÓ pode ser LIDO se houver consentimento ativo (verifique antes).
3. Prontuário SÓ pode ser ATUALIZADO se houver consentimento ativo (US03).
4. Se o consentimento for REVOGADO, o prontuário continua no banco mas fica
   bloqueado para edição e com dados sensíveis ocultos.

Toda verificação de consentimento deve acontecer no CONTROLLER antes de
chamar qualquer método desse model. O model assume que a permissão já foi checada.
"""

from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class ProntuarioModel:
    """
    Gerencia o prontuário social integrado das pessoas atendidas.

    O prontuário é a visão mais rica do sistema — consolida pessoa,
    atendimentos, encaminhamentos e status em uma única consulta.
    """

    @staticmethod
    def criar(pessoa_id: int, consentimento_id: int, dados: dict = None) -> dict | None:
        """
        Cria o prontuário social da pessoa.

        Só pode ser chamado APÓS o controller verificar que existe
        um consentimento ativo para essa pessoa (US02).

        Args:
            pessoa_id (int): ID da pessoa.
            consentimento_id (int): ID do consentimento ativo que autoriza a criação.
            dados (dict, optional): Dados iniciais: 'diagnostico_social', 'observacoes'.

        Returns:
            dict | None: Prontuário recém-criado.

        TODO (estagiário): INSERT INTO prontuario (pessoa_id, consentimento_id,
                           diagnostico_social, observacoes) VALUES (%s, %s, %s, %s).
                           A coluna `pessoa_id` tem UNIQUE constraint — uma pessoa
                           só pode ter UM prontuário. Se tentar criar dois,
                           o banco rejeita. Trate isso como HTTP 409 no controller.
        """
        # TODO: Implementar
        raise NotImplementedError("ProntuarioModel.criar() ainda não foi implementado.")

    @staticmethod
    def buscar_completo_por_pessoa(pessoa_id: int) -> dict | None:
        """
        Retorna o prontuário integrado completo da pessoa (US05).

        Esse é o endpoint mais pesado do sistema — faz múltiplos JOINs para
        consolidar em uma única resposta: dados da pessoa, lista de atendimentos,
        lista de encaminhamentos formais e status atual de risco.

        Args:
            pessoa_id (int): ID da pessoa.

        Returns:
            dict | None: Prontuário completo com dados aninhados ou None se não existir.

        TODO (estagiário): Essa query vai ser a mais complexa que você vai escrever.
                           Estruture assim (pode ser em partes ou uma query grande):

                           PARTE 1 — Dados do prontuário + pessoa:
                           SELECT pr.*, pe.apelido, pe.nome_real, pe.nivel_risco, ...
                           FROM prontuario pr
                           JOIN pessoa_rua pe ON pr.pessoa_id = pe.id
                           WHERE pr.pessoa_id = %s

                           PARTE 2 — Atendimentos (query separada):
                           SELECT at.*, p.nome AS profissional_nome
                           FROM atendimento at
                           JOIN profissional p ON at.profissional_id = p.id
                           WHERE at.pessoa_id = %s
                           ORDER BY at.realizado_em DESC

                           PARTE 3 — Encaminhamentos formais (query separada):
                           SELECT * FROM encaminhamento
                           WHERE atendimento_id IN (
                               SELECT id FROM atendimento WHERE pessoa_id = %s
                           ) AND prontuario_id IS NOT NULL

                           Monte o resultado como um dict com chaves aninhadas:
                           { 'prontuario': {...}, 'atendimentos': [...], 'encaminhamentos': [...] }
        """
        # TODO: Implementar
        raise NotImplementedError(
            "ProntuarioModel.buscar_completo_por_pessoa() ainda não foi implementado."
        )

    @staticmethod
    def atualizar(prontuario_id: int, dados: dict) -> dict | None:
        """
        Atualiza informações do prontuário (diagnósticos, observações sociais).

        Só pode ser chamado APÓS o controller verificar que o consentimento
        ainda está ativo. Se revogado, o controller retorna 403 antes de
        chegar aqui (US03).

        Args:
            prontuario_id (int): ID do prontuário.
            dados (dict): Campos a atualizar: 'diagnostico_social', 'observacoes'.

        Returns:
            dict | None: Prontuário atualizado ou None se não encontrado.

        TODO (estagiário): UPDATE prontuario SET diagnostico_social=%s,
                           observacoes=%s WHERE id=%s.
                           Retorne o prontuário atualizado via SELECT após o UPDATE.
        """
        # TODO: Implementar
        raise NotImplementedError(
            "ProntuarioModel.atualizar() ainda não foi implementado."
        )
