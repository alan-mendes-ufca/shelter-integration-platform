from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo
from datetime import datetime, timedelta


class ConsentimentoModel(Database):
    """
    Gerencia o ciclo de vida do consentimento LGPD das pessoas atendidas.

    Fluxo esperado:
        1. POST /consentimentos     → criar()       → ativo=True
        2. GET  /consentimentos/:id → buscar_ativo() → verifica se ainda é True
        3. PUT  /consentimentos/:id/revogar → revogar() → ativo=FALSE, revogado_em=NOW()
    """

    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        """
        Registra o consentimento formal de uma pessoa para tratamento de dados.

        Campos principais da tabela:
        - pessoa_id  (aponta para pessoa_rua_id)
        - data_assinatura DATETIME,
        - ativo
        - validade

        """
        #  Implementar
        observacao = dados.get("observacao")
        pessoa_id = dados.get("pessoa_id")

        if not pessoa_id:
            raise ValueError(
                "O ID da pessoa é obrigatório para registrar o consentimento"
            )

        data_atual = datetime.now()
        data_validade = data_atual + timedelta(days=365)

        query_insert = """
            INSERT INTO consentimento (pessoa_id, ativo, validade, observacao, data_assinatura)
            VALUES (%s, True, %s, %s, CURRENT_TIMESTAMP)
        """

        params_insert = (pessoa_id, data_validade, observacao)
        cls.query(query_insert, params_insert)

        return cls.buscar_ativo_por_pessoa(pessoa_id)

    @classmethod
    def buscar_ativo_por_pessoa(cls, pessoa_id: int) -> dict | None:
        query = "SELECT * FROM consentimento where pessoa_id = %s AND ativo is True  AND validade > NOW()"
        params = (pessoa_id,)

        rows = cls.query(query, params)

        if rows:
            return rows[0]

        else:
            return None

    @classmethod
    def revogar_consentimento(
        cls, pessoa_id: int, observacao: str = None
    ) -> dict | None:
        """
        O botão de emergência da LGPD.
        Muda o ativo para False imediatamente, independente da validade.
        """
        # A query atualiza a linha específica daquela pessoa
        query_update = """
            UPDATE consentimento 
            SET ativo = False, observacao = %s 
            WHERE pessoa_id = %s
        """

        params_update = (observacao, pessoa_id)

        cls.query(query_update, params_update)

        query_select = "SELECT * FROM consentimento WHERE pessoa_id = %s"
        rows = cls.query(query_select, (pessoa_id,))

        if rows:
            return rows[0]
        return None

    @classmethod
    def reativar_consentimento(
        cls, pessoa_id: int, observacao: str = None
    ) -> dict | None:
        """
        O botão de emergência da LGPD.
        Muda o ativo para True imediatamente.
        """
        data_atual = datetime.now()
        data_validade = data_atual + timedelta(days=365)
        # A query atualiza a linha específica daquela pessoa
        query_update = """
            UPDATE consentimento 
            SET ativo = True,
                observacao = %s,
                validade = %s,
                data_assinatura = CURRENT_TIMESTAMP
            WHERE pessoa_id = %s
        """

        params_update = (observacao, data_validade, pessoa_id)

        cls.query(query_update, params_update)

        query_select = "SELECT * FROM consentimento WHERE pessoa_id = %s"
        rows = cls.query(query_select, (pessoa_id,))

        if rows:
            return rows[0]
        return None

    @classmethod
    def buscar_por_pessoa(cls, pessoa_id: int) -> dict | None:
        """
        Busca o estado bruto do consentimento da pessoa, não importa se está ativo,
        revogado ou vencido.
        """
        query = "SELECT * FROM consentimento WHERE pessoa_id = %s"
        rows = cls.query(query, (pessoa_id,))

        if rows:
            return rows[0]
        return None
