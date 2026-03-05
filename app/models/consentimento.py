"""
Model: Consentimento
====================

Estagiário, esse model implementa o guardião legal do sistema baseado na LGPD.

Ponto crítico que você precisa gravar:
- Consentimento NÃO é sobre se a pessoa pode ser atendida (isso é sempre sim).
- Consentimento é sobre se os dados SENSÍVEIS dela podem ser registrados e vistos.
- Sem consentimento → atendimento normal, mas sem prontuário.
- Com consentimento → prontuário liberado para criação e acesso.
- Consentimento revogado → prontuário existente vira read-only, dados sensíveis ocultos.

Essa lógica de bloqueio é aplicada nos controllers, mas os dados que
suportam ela (campo `ativo`, `revogado_em`) ficam aqui no model.
"""

from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class ConsentimentoModel:
    """
    Gerencia o ciclo de vida do consentimento LGPD das pessoas atendidas.

    Fluxo esperado:
        1. POST /consentimentos     → criar()       → ativo=True
        2. GET  /consentimentos/:id → buscar_ativo() → verifica se ainda é True
        3. PUT  /consentimentos/:id/revogar → revogar() → ativo=False, revogado_em=NOW()
    """

    @staticmethod
    def criar(pessoa_id: int, observacao: str = None) -> dict | None:
        """
        Registra o consentimento formal de uma pessoa para tratamento de dados.

        Ao criar um consentimento, o prontuário social dessa pessoa pode
        ser criado e acessado (US02).

        Args:
            pessoa_id (int): ID da pessoa que está dando consentimento.
            observacao (str, optional): Contexto ou observação do momento do consentimento.

        Returns:
            dict | None: Registro do consentimento criado.

        TODO (estagiário): Antes de inserir, verifique se já existe um consentimento
                           ATIVO para essa pessoa. Não faz sentido ter dois ativos
                           ao mesmo tempo. Se existir, retorne o existente ou lance
                           um erro com mensagem clara. Combine isso com o controller.
        """
        # TODO: Implementar
        raise NotImplementedError("ConsentimentoModel.criar() ainda não foi implementado.")

    @staticmethod
    def buscar_ativo_por_pessoa(pessoa_id: int) -> dict | None:
        """
        Verifica se existe consentimento ATIVO para a pessoa informada.

        Esse método é chamado automaticamente pelo ProntuarioModel antes
        de qualquer exibição ou edição de dados sensíveis.

        Args:
            pessoa_id (int): ID da pessoa.

        Returns:
            dict | None: Consentimento ativo ou None se não existir/revogado.

        TODO (estagiário): SELECT com WHERE pessoa_id = %s AND ativo = TRUE.
                           Retorne result[0] se encontrar, None se a lista vier vazia.
        """
        # TODO: Implementar
        raise NotImplementedError("ConsentimentoModel.buscar_ativo_por_pessoa() ainda não foi implementado.")

    @staticmethod
    def revogar(consentimento_id: int, observacao: str = None) -> dict | None:
        """
        Registra a revogação do consentimento (US03).

        Consequências da revogação (gerenciadas nos controllers):
        - O prontuário existente passa a ser somente leitura.
        - Dados sensíveis ficam ocultos nas respostas da API.
        - Novos atendimentos simples continuam sendo possíveis.

        Args:
            consentimento_id (int): ID do consentimento a ser revogado.
            observacao (str, optional): Motivo ou contexto da revogação.

        Returns:
            dict | None: Consentimento atualizado (agora com ativo=False).

        TODO (estagiário): UPDATE consentimento SET ativo=FALSE, revogado_em=NOW(),
                           observacao=%s WHERE id=%s AND ativo=TRUE.
                           Se nenhuma linha for afetada (rowcount=0), significa que
                           o consentimento já estava revogado ou não existe.
                           Trate esse caso no controller retornando 404 ou 409.
        """
        # TODO: Implementar
        raise NotImplementedError("ConsentimentoModel.revogar() ainda não foi implementado.")

    @staticmethod
    def historico_por_pessoa(pessoa_id: int) -> list[dict]:
        """
        Retorna o histórico COMPLETO de consentimentos e revogações de uma pessoa.

        Usado para auditoria e compliance com a LGPD. Todo evento de
        consentimento ou revogação deve ser rastreável.

        Args:
            pessoa_id (int): ID da pessoa.

        Returns:
            list[dict]: Lista de todos os registros de consentimento, em ordem
                        cronológica decrescente (mais recente primeiro).

        TODO (estagiário): SELECT * FROM consentimento WHERE pessoa_id = %s
                           ORDER BY registrado_em DESC.
        """
        # TODO: Implementar
        raise NotImplementedError("ConsentimentoModel.historico_por_pessoa() ainda não foi implementado.")


