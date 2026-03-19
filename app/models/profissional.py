from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo
from infra.erros import ValidationError


class ProfissionalModel(Database):
    """
    Gerencia o cadastro de profissionais que operam o sistema.

    Profissionais são: assistentes sociais, educadores sociais,
    psicólogos, coordenadores, etc.
    """

    @staticmethod
    def _validar_id_pessoa_obrigatorio(id_pessoa: object) -> object:
        if not id_pessoa:
            raise ValidationError(
                message="O campo 'id_pessoa' é obrigatório.",
                action="Informe um valor válido para 'id_pessoa'.",
            )
        return id_pessoa

    @staticmethod
    def _validar_cargo_obrigatorio(cargo: object) -> str:
        if not cargo or not str(cargo).strip():
            raise ValidationError(
                message="O campo 'cargo' é obrigatório.",
                action="Informe um valor válido para 'cargo'.",
            )
        return str(cargo).strip()

    @staticmethod
    def _normalizar_registro_conselho(registro_conselho: object) -> object:
        if registro_conselho:
            return str(registro_conselho).strip()
        return registro_conselho

    @classmethod
    def criar(cls, dados: dict) -> dict | None:

        id_pessoa = cls._validar_id_pessoa_obrigatorio(dados.get("id_pessoa"))
        cargo = cls._validar_cargo_obrigatorio(dados.get("cargo"))
        registro_conselho = cls._normalizar_registro_conselho(
            dados.get("registro_conselho")
        )

        query_insert = """
            INSERT INTO profissional(id_pessoa, cargo, registro_conselho)
            VALUES (%s, %s, %s)
        """

        params_insert = (id_pessoa, cargo, registro_conselho)

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
