from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo
from infra.erros import ValidationError


class ConsentimentoModel(Database):
    """
    Gerencia o ciclo de vida do consentimento LGPD das pessoas atendidas.

    Fluxo esperado:
        1. POST /consentimentos     → criar()       → ativo=True
        2. GET  /consentimentos/:id → buscar_ativo() → verifica se ainda é True
        3. PUT  /consentimentos/:id/revogar → revogar() → ativo=FALSE, revogado_em=NOW()
    """

    @staticmethod
    def _validar_pessoa_id(pessoa_id: object) -> int:
        try:
            pessoa_id_int = int(pessoa_id)
        except (TypeError, ValueError) as err:
            raise ValidationError(
                message="O campo 'pessoa_id' é obrigatório e deve ser numérico.",
                action="Informe um ID de pessoa válido.",
            ) from err

        if pessoa_id_int <= 0:
            raise ValidationError(
                message="O campo 'pessoa_id' deve ser maior que zero.",
                action="Informe um ID de pessoa válido.",
            )

        return pessoa_id_int

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
        pessoa_id = cls._validar_pessoa_id(dados.get("pessoa_id"))

        query_insert = """
            INSERT INTO consentimento (id_pessoa_rua, ativo, observacao)
            VALUES (%s, TRUE, %s)
        """

        params_insert = (pessoa_id, observacao)
        cls.query(query_insert, params_insert)

        return cls.buscar_ativo_por_pessoa(pessoa_id)

    @classmethod
    def buscar_ativo_por_pessoa(cls, pessoa_id: int) -> dict | None:
        pessoa_id = cls._validar_pessoa_id(pessoa_id)
        query = "SELECT * FROM consentimento WHERE id_pessoa_rua = %s AND ativo = TRUE"
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
            SET ativo = FALSE, observacao = %s, revogado_em = CURRENT_TIMESTAMP
            WHERE id_pessoa_rua = %s AND ativo = TRUE
        """

        pessoa_id = cls._validar_pessoa_id(pessoa_id)
        params_update = (observacao, pessoa_id)

        cls.query(query_update, params_update)

        query_select = "SELECT * FROM consentimento WHERE id_pessoa_rua = %s"
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
        # A query atualiza a linha específica daquela pessoa
        query_update = """
            UPDATE consentimento
            SET ativo = True,
                observacao = %s,
                registrado_em = CURRENT_TIMESTAMP,
                revogado_em = NULL
            WHERE id_pessoa_rua = %s
        """

        pessoa_id = cls._validar_pessoa_id(pessoa_id)
        params_update = (observacao, pessoa_id)

        cls.query(query_update, params_update)

        query_select = "SELECT * FROM consentimento WHERE id_pessoa_rua = %s"
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
        pessoa_id = cls._validar_pessoa_id(pessoa_id)
        query = "SELECT * FROM consentimento WHERE id_pessoa_rua = %s"
        rows = cls.query(query, (pessoa_id,))

        if rows:
            return rows[0]
        return None

    @classmethod
    def listar_historico_por_pessoa(cls, pessoa_id: int) -> list[dict]:
        """Retorna o histórico completo de consentimentos de uma pessoa."""
        pessoa_id = cls._validar_pessoa_id(pessoa_id)
        query = """
            SELECT *
            FROM consentimento
            WHERE id_pessoa_rua = %s
            ORDER BY registrado_em DESC, id_consentimento DESC
        """
        return cls.query(query, (pessoa_id,)) or []
