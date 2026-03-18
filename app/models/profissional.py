from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class ProfissionalModel(Database):
    """
    Gerencia o cadastro de profissionais que operam o sistema.

    Profissionais são: assistentes sociais, educadores sociais,
    psicólogos, coordenadores, etc.
    """

    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        id_pessoa = dados.get("id_pessoa")
        cargo = dados.get("cargo")
        registro_conselho = dados.get("registro_conselho")

        if not id_pessoa:
            raise ValueError("O campo 'id_pessoa' é OBRIGATÓRIO.")

        if not cargo or not str(cargo).strip():
            raise ValueError("O campo 'cargo' é OBRIGATÓRIO.")

        if registro_conselho:
            registro_conselho = str(registro_conselho).strip()

        query_insert = """
            INSERT INTO profissional(id_pessoa, cargo, registro_conselho)
            VALUES (%s, %s, %s)
        """

        params_insert = (id_pessoa, str(cargo).strip(), registro_conselho)

        cls.query(query_insert, params_insert)

        query_select = """
            SELECT p.id_profissional, p.id_pessoa, pe.nome, p.cargo, p.registro_conselho
            FROM profissional p
            INNER JOIN pessoa pe ON p.id_pessoa = pe.id_pessoa
            WHERE p.id_pessoa = %s
            ORDER BY p.id_profissional DESC
            LIMIT 1
        """

        rows = cls.query(query_select, (id_pessoa,))

        if rows:
            return rows[0]
        return None

    @classmethod
    def buscar_por_id(cls, profissional_id: int) -> dict | None:

        query = """
            SELECT p.id_profissional, p.id_pessoa, pe.nome, p.cargo, p.registro_conselho 
            FROM profissional p
            INNER JOIN pessoa pe ON p.id_pessoa = pe.id_pessoa
            WHERE p.id_profissional = %s
        """
        params = (profissional_id,)
        rows = cls.query(query, params)

        if rows:
            return rows[0]
        return None

    @classmethod
    def listar(cls) -> list[dict]:
        query = """
            SELECT p.id_profissional, p.id_pessoa, pe.nome, p.cargo, p.registro_conselho 
            FROM profissional p
            INNER JOIN pessoa pe ON p.id_pessoa = pe.id_pessoa
            ORDER BY p.id_profissional DESC
        """
        rows = cls.query(query)
        return rows or []
