from infra.database import Database


class PessoaRuaModel(Database):
    """
    Model da tabela `pessoa_rua`.

    Responsável por acessar e manipular os dados de pessoas em situação de rua:
    criar cadastro, buscar por ID, buscar por apelido, atualizar dados e atualizar
    nível de risco.

    Campos principais da tabela:
    - id_pessoa_rua
    - apelido
    - descricao_fisica
    - nome_civil
    - cpf_opcional
    - nivel_risco
    """

    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        query_insert = """
            INSERT INTO pessoa_rua(apelido, descricao_fisica, nome_civil, cpf_opcional)
            VALUES (%s, %s, %s, %s)
        """
        params_insert = (
            dados["apelido"],
            dados.get("descricao_fisica"),
            dados.get("nome_civil"),
            dados.get("cpf_opcional"),
        )
        cls.query(query_insert, params_insert)

        if dados.get("cpf_opcional"):
            query_select = "SELECT * FROM pessoa_rua WHERE cpf_opcional = %s LIMIT 1"
            params_select = (dados["cpf_opcional"],)

        else:
            query_select = """
                SELECT * FROM pessoa_rua
                WHERE apelido = %s
                ORDER BY id_pessoa_rua DESC
                LIMIT 1
            """
            params_select = (dados["apelido"],)

        rows = cls.query(query_select, params_select)

        if rows:
            return rows[0]
        else:
            return None

    @classmethod
    def buscar_por_id(cls, pessoa_id: int) -> dict | None:
        query = "SELECT * FROM pessoa_rua WHERE id_pessoa_rua = %s"
        params = (pessoa_id,)

        rows = cls.query(query, params)

        if rows:
            return rows[0]

        else:
            return None

    @classmethod
    def buscar_por_apelido(cls, apelido: str) -> list[dict]:
        termo = f"%{apelido}%"
        query = """
                SELECT * FROM pessoa_rua
                WHERE apelido LIKE %s OR descricao_fisica LIKE %s
                ORDER BY id_pessoa_rua DESC
            """
        params = (termo, termo)

        rows = cls.query(query, params)
        return rows or []

    @classmethod
    def atualizar(cls, pessoa_id: int, dados: dict) -> dict | None:
        campos = []
        valores = []
        permitidos = ["apelido", "descricao_fisica", "nome_civil", "cpf_opcional"]

        for campo in permitidos:
            if campo in dados:
                campos.append(f"{campo} = %s")
                valores.append(dados[campo])

        if not campos:
            return cls.buscar_por_id(pessoa_id)

        valores.append(pessoa_id)
        query_update = f"UPDATE pessoa_rua SET {', '.join(campos)} WHERE id_pessoa_rua = %s"
        params_update = tuple(valores)

        cls.query(query_update, params_update)

        return cls.buscar_por_id(pessoa_id)

    @classmethod
    def atualizar_risco(cls, pessoa_id: int, nivel_risco: str) -> dict | None:
        niveis_validos = {"baixo", "medio", "alto", "critico"}

        if nivel_risco not in niveis_validos:
            raise ValueError(
                f"nivel_risco inválido: '{nivel_risco}'."
                f"Valores válidos: {sorted(niveis_validos)}"
            )

        query_update = """
                UPDATE pessoa_rua
                SET nivel_risco = %s
                WHERE id_pessoa_rua = %s
            """
        params_update = (nivel_risco, pessoa_id)

        cls.query(query_update, params_update)

        return cls.buscar_por_id(pessoa_id)

    @classmethod
    def listar_com_filtros(
        cls,
        apelido: str | None = None,
        nome_civil: str | None = None,
        nivel_risco: str | None = None,
    ) -> list[dict]:
        query_base = "SELECT * FROM pessoa_rua"
        filtros = []
        valores = []

        if apelido:
            filtros.append("apelido LIKE %s")
            valores.append(f"%{apelido}%")

        if nome_civil:
            filtros.append("nome_civil LIKE %s")
            valores.append(f"%{nome_civil}%")

        if nivel_risco:
            filtros.append("nivel_risco = %s")
            valores.append(nivel_risco)

        if filtros:
            query_base += " WHERE " + " AND ".join(filtros)

        query_base += " ORDER BY id_pessoa_rua DESC"

        rows = cls.query(query_base, tuple(valores))
        return rows or []
