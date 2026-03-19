from infra.database import Database
from infra.erros import NotFoundError, ValidationError


class EncaminhamentoModel(Database):
    STATUS_VALIDOS = {"pendente", "atendido", "resolvido", "cancelado"}
    PRIORIDADES_VALIDAS = {"baixa", "media", "alta"}

    @staticmethod
    def _validar_inteiro_positivo(valor: object, campo: str) -> int:
        try:
            valor_int = int(valor)
        except (TypeError, ValueError) as err:
            raise ValidationError(
                message=f"O campo '{campo}' deve ser numérico.",
                action=f"Informe um valor inteiro válido para '{campo}'.",
            ) from err

        if valor_int <= 0:
            raise ValidationError(
                message=f"O campo '{campo}' deve ser maior que zero.",
                action=f"Informe um valor inteiro válido para '{campo}'.",
            )

        return valor_int

    @classmethod
    def _buscar_por_id(cls, encaminhamento_id: int) -> dict | None:
        rows = cls.query(
            "SELECT * FROM encaminhamento WHERE id_encaminhamento_pk = %s",
            (encaminhamento_id,),
        )
        return rows[0] if rows else None

    @staticmethod
    def _validar_orgao_destino(orgao_destino: object) -> str:
        orgao_destino = str(orgao_destino or "").strip()
        if not orgao_destino:
            raise ValidationError(
                message="O campo 'orgaoDestino' é obrigatório.",
                action="Informe o órgão de destino do encaminhamento.",
            )
        return orgao_destino

    @staticmethod
    def _validar_motivo(motivo: object) -> str:
        motivo = str(motivo or "").strip()
        if not motivo:
            raise ValidationError(
                message="O campo 'motivo' é obrigatório.",
                action="Informe o motivo do encaminhamento.",
            )
        return motivo

    @classmethod
    def _validar_prioridade(cls, prioridade: object) -> str:
        prioridade = str(prioridade or "").strip().lower()
        if prioridade not in cls.PRIORIDADES_VALIDAS:
            raise ValidationError(
                message="O campo 'prioridade' é inválido.",
                action="Use uma das prioridades: baixa, media ou alta.",
            )
        return prioridade

    @classmethod
    def _validar_status(cls, status: object) -> str:
        status = str(status or "").strip().lower()
        if status not in cls.STATUS_VALIDOS:
            raise ValidationError(
                message="Status de encaminhamento inválido.",
                action="Use: pendente, atendido, resolvido ou cancelado.",
            )
        return status

    @classmethod
    def _validar_atendimento_existe(cls, id_atendimento: int) -> None:
        atendimento = cls.query(
            "SELECT id_atendimento FROM atendimento WHERE id_atendimento = %s",
            (id_atendimento,),
        )
        if not atendimento:
            raise NotFoundError(
                message="Atendimento não encontrado para encaminhamento.",
                action="Verifique o 'id_atendimento_fk' informado.",
            )

    @staticmethod
    def _validar_cancelamento_permitido(status_acompanhamento: str) -> None:
        if status_acompanhamento != "pendente":
            raise ValidationError(
                message="Somente encaminhamentos pendentes podem ser cancelados.",
                action="Atualize o status conforme o fluxo de acompanhamento.",
            )

    @classmethod
    def criar(cls, dados):

        id_atendimento = cls._validar_inteiro_positivo(
            dados.get("id_atendimento_fk"), "id_atendimento_fk"
        )
        orgao_destino = cls._validar_orgao_destino(dados.get("orgaoDestino"))
        motivo = cls._validar_motivo(dados.get("motivo"))
        prioridade = cls._validar_prioridade(dados.get("prioridade"))
        cls._validar_atendimento_existe(id_atendimento)

        sql = """
            INSERT INTO encaminhamento
            (id_atendimento_fk, orgaoDestino, motivo, prioridade, status_acompanhamento)
            VALUES (%s, %s, %s, %s, 'pendente')
        """
        params = (
            id_atendimento,
            orgao_destino,
            motivo,
            prioridade,
        )
        encaminhamento_id = cls.query(sql, params)
        return cls._buscar_por_id(encaminhamento_id)

    @classmethod
    def listar_por_pessoa(cls, id_pessoa_rua: int) -> list[dict]:
        id_pessoa_rua = cls._validar_inteiro_positivo(id_pessoa_rua, "id_pessoa_rua")
        sql = """
            SELECT e.* FROM encaminhamento e
            JOIN atendimento a ON e.id_atendimento_fk = a.id_atendimento
            WHERE a.id_pessoa_rua = %s
        """
        return cls.query(sql, (id_pessoa_rua,)) or []

    @classmethod
    def listar_por_status(cls, status: str) -> list[dict]:
        status = cls._validar_status(status)

        sql = """
            SELECT * FROM encaminhamento
            WHERE status_acompanhamento = %s
        """
        return cls.query(sql, (status,)) or []

    @classmethod
    def atualizar_status(
        cls, id_encaminhamento_pk: int, novo_status: str
    ) -> dict | None:
        encaminhamento_id = cls._validar_inteiro_positivo(
            id_encaminhamento_pk, "id_encaminhamento_pk"
        )
        novo_status = cls._validar_status(novo_status)

        encaminhamento_atual = cls._buscar_por_id(encaminhamento_id)
        if not encaminhamento_atual:
            raise NotFoundError(
                message="Encaminhamento não encontrado.",
                action="Verifique o ID informado.",
            )

        sql = """
            UPDATE encaminhamento
            SET status_acompanhamento = %s
            WHERE id_encaminhamento_pk = %s
        """
        params = (novo_status, encaminhamento_id)
        cls.query(sql, params)
        return cls._buscar_por_id(encaminhamento_id)

    @classmethod
    def cancelar(cls, id_encaminhamento_pk: int) -> dict | None:
        encaminhamento_id = cls._validar_inteiro_positivo(
            id_encaminhamento_pk, "id_encaminhamento_pk"
        )
        encaminhamento_atual = cls._buscar_por_id(encaminhamento_id)
        if not encaminhamento_atual:
            raise NotFoundError(
                message="Encaminhamento não encontrado.",
                action="Verifique o ID informado.",
            )

        cls._validar_cancelamento_permitido(
            encaminhamento_atual.get("status_acompanhamento")
        )

        sql = """
            UPDATE encaminhamento
            SET status_acompanhamento = 'cancelado'
            WHERE id_encaminhamento_pk = %s AND status_acompanhamento = 'pendente'
        """
        cls.query(sql, (encaminhamento_id,))
        return cls._buscar_por_id(encaminhamento_id)
