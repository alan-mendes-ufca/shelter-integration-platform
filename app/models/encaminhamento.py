from infra.database import Database


class EncaminhamentoModel(Database):
    @classmethod
    def criar(cls, dados):
        sql = """
            INSERT INTO encaminhamento
            (id_atendimento_fk, orgaoDestino, motivo, prioridade, status_acompanhamento)
            VALUES (%s, %s, %s, %s, 'pendente')
        """
        params = (
            dados["id_atendimento_fk"],
            dados["orgaoDestino"],
            dados["motivo"],
            dados["prioridade"],
        )
        return Database.query(sql, params)

    @classmethod
    def listar_por_pessoa(cls, id_pessoa_rua: int) -> list[dict]:
        sql = """
            SELECT e.* FROM encaminhamento e
            JOIN atendimento a ON e.id_atendimento_fk = a.id_atendimento
            WHERE a.id_pessoa_rua = %s
        """
        return Database.query(sql, (id_pessoa_rua,))

    @classmethod
    def listar_por_status(cls, status: str) -> list[dict]:
        sql = """
            SELECT * FROM encaminhamento
            WHERE status_acompanhamento = %s
        """
        return Database.query(sql, (status,))

    @classmethod
    def atualizar_status(
        cls, id_encaminhamento_pk: int, novo_status: str
    ) -> dict | None:
        sql = """
            UPDATE encaminhamento
            SET status_acompanhamento = %s
            WHERE id_encaminhamento_pk = %s
        """
        params = (novo_status, id_encaminhamento_pk)
        return Database.query(sql, params)

    @classmethod
    def cancelar(cls, id_encaminhamento_pk: int) -> dict | None:
        sql = """
            UPDATE encaminhamento
            SET status_acompanhamento = 'cancelado'
            WHERE id_encaminhamento_pk = %s AND status_acompanhamento = 'pendente'
        """
        return Database.query(sql, (id_encaminhamento_pk,))
