"""
Model: Encaminhamento
=====================

Estagiário, esse model tem uma lógica de negócio importante que você precisa
entender antes de implementar qualquer coisa:

Existem DOIS tipos de encaminhamento:

1. FORMAL      → prontuario_id preenchido → pessoa tem consentimento ativo
                  → dados completos registrados → rastreável no prontuário

2. EMERGÊNCIA  → prontuario_id = NULL → sem necessidade de consentimento
                  → usado em crises de saúde, risco de vida imediato
                  → dados mínimos, mas ainda vinculado a um atendimento

O campo `tipo` (ENUM: 'formal' ou 'emergencia') é preenchido pela aplicação
com base na presença ou ausência do `prontuario_id`. O frontend não define isso,
a aplicação define. Isso é uma regra de negócio, não uma escolha do usuário.

A rastreabilidade do encaminhamento é o coração do US10:
"Sem esse módulo, os encaminhamentos ficam apenas como anotações verbais."
"""

from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class EncaminhamentoModel:
    """
    Gerencia os encaminhamentos para a rede externa de apoio social.

    Tipos de destino: CRAS, CREAS, UBS, Hospital, Delegacia, etc.
    """

    @staticmethod
    def criar(dados: dict) -> dict | None:
        """
        Gera um novo encaminhamento vinculado a um atendimento (US10).

        O tipo (formal/emergência) é determinado automaticamente:
        - prontuario_id presente → 'formal'
        - prontuario_id ausente  → 'emergencia'

        Args:
            dados (dict): Dados do encaminhamento.
                          Obrigatórios: 'atendimento_id', 'destino', 'motivo'
                          Opcional:     'prontuario_id' (None = emergência)

        Returns:
            dict | None: Encaminhamento recém-criado com o tipo determinado.

        TODO (estagiário): Antes do INSERT, determine o `tipo`:
                           tipo = 'formal' if dados.get('prontuario_id') else 'emergencia'
                           Inclua isso no INSERT junto com os outros campos.
                           O status inicial é sempre 'pendente'.
        """
        # TODO: Implementar
        raise NotImplementedError("EncaminhamentoModel.criar() ainda não foi implementado.")

    @staticmethod
    def listar_por_pessoa(pessoa_id: int) -> list[dict]:
        """
        Lista todos os encaminhamentos (formais e de emergência) de uma pessoa.

        Permite ao profissional ver o que já foi solicitado e evitar duplicidade.

        Args:
            pessoa_id (int): ID da pessoa.

        Returns:
            list[dict]: Lista de encaminhamentos ordenados por data decrescente.

        TODO (estagiário): O encaminhamento não tem pessoa_id diretamente.
                           Você vai precisar chegar à pessoa via atendimento:
                           SELECT enc.*
                           FROM encaminhamento enc
                           JOIN atendimento at ON enc.atendimento_id = at.id
                           WHERE at.pessoa_id = %s
                           ORDER BY enc.criado_em DESC
        """
        # TODO: Implementar
        raise NotImplementedError("EncaminhamentoModel.listar_por_pessoa() ainda não foi implementado.")

    @staticmethod
    def listar_por_status(status: str) -> list[dict]:
        """
        Filtra encaminhamentos por status para monitoramento pelo gestor.

        Args:
            status (str): Um de: 'pendente', 'atendido', 'resolvido', 'cancelado'.

        Returns:
            list[dict]: Lista de encaminhamentos com o status informado.

        TODO (estagiário): SELECT * FROM encaminhamento WHERE status = %s
                           ORDER BY criado_em ASC (pendentes mais antigos primeiro — urgência).
                           Valide o `status` no controller antes de chegar aqui.
        """
        # TODO: Implementar
        raise NotImplementedError("EncaminhamentoModel.listar_por_status() ainda não foi implementado.")

    @staticmethod
    def atualizar_status(encaminhamento_id: int, novo_status: str) -> dict | None:
        """
        Atualiza o status do encaminhamento no ciclo de vida rastreável.

        Ciclo esperado: pendente → atendido → resolvido
        Fluxo alternativo: pendente → cancelado (com motivo obrigatório)

        Args:
            encaminhamento_id (int): ID do encaminhamento.
            novo_status (str): Novo status a aplicar.

        Returns:
            dict | None: Encaminhamento atualizado ou None se não encontrado.

        TODO (estagiário): Valide a transição de status no controller:
                           - Não faz sentido ir de 'resolvido' de volta para 'pendente'.
                           - 'cancelado' deve exigir o campo `cancelamento_motivo`.
                           Aqui no model, apenas execute o UPDATE.
        """
        # TODO: Implementar
        raise NotImplementedError("EncaminhamentoModel.atualizar_status() ainda não foi implementado.")

    @staticmethod
    def cancelar(encaminhamento_id: int, motivo_cancelamento: str) -> dict | None:
        """
        Cancela um encaminhamento emitido indevidamente, registrando o motivo.

        O cancelamento é uma operação auditada — o motivo é obrigatório
        e fica registrado no campo `cancelamento_motivo`.

        Args:
            encaminhamento_id (int): ID do encaminhamento.
            motivo_cancelamento (str): Motivo do cancelamento (obrigatório para auditoria).

        Returns:
            dict | None: Encaminhamento cancelado ou None se não encontrado.

        TODO (estagiário): UPDATE encaminhamento
                           SET status='cancelado', cancelamento_motivo=%s
                           WHERE id=%s AND status='pendente'.
                           Só cancele encaminhamentos que ainda estão pendentes.
                           Se já estiver 'atendido' ou 'resolvido', retorne erro 409
                           no controller com mensagem: "Encaminhamento já processado, não pode ser cancelado."
        """
        # TODO: Implementar
        raise NotImplementedError("EncaminhamentoModel.cancelar() ainda não foi implementado.")


