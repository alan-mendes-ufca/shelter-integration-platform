from infra.database import Database
from infra.erros import ValidationError


class PessoaModel(Database):
    """
    Model da tabela `pessoa`.

    Responsável por acessar e manipular os dados de pessoas usuárias do sistema:
    criar cadastro, buscar por ID, atualizar dados e listar registros.

    Campos principais da tabela:
    - id_pessoa
    - nome
    - senha
    """

    @staticmethod
    def _texto_obrigatorio(valor: object, campo: str) -> str:
        texto = str(valor or "").strip()
        if not texto:
            raise ValidationError(
                message=f"{campo} é obrigatório.",
                action=f"Preencha o campo '{campo}' com um valor válido.",
            )
        return texto

    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        nome = cls._texto_obrigatorio(dados.get("nome"), "nome")
        senha = cls._texto_obrigatorio(dados.get("senha"), "senha")

        query_insert = """
        INSERT INTO pessoa(nome, senha)
        VALUES(%s, %s)
        """

        id_pessoa = cls.query(query_insert, (nome, senha))

        return cls.buscar_por_id(id_pessoa)

    @classmethod
    def buscar_por_id(cls, pessoa_id: int) -> dict | None:
        query = "SELECT * FROM pessoa WHERE id_pessoa = %s"
        params = (pessoa_id,)

        rows = cls.query(query, params)

        if rows:
            return rows[0]

        else:
            return None

    @classmethod
    def atualizar(cls, pessoa_id: int, dados: dict) -> dict | None:
        campos = []
        valores = []

        if "nome" in dados:
            nome = cls._texto_obrigatorio(dados.get("nome"), "nome")
            campos.append("nome = %s")
            valores.append(nome)

        if "senha" in dados:
            senha = cls._texto_obrigatorio(dados.get("senha"), "senha")
            campos.append("senha = %s")
            valores.append(senha)

        if not campos:
            return cls.buscar_por_id(pessoa_id)

        valores.append(pessoa_id)
        query_update = f"UPDATE pessoa SET {', '.join(campos)} WHERE id_pessoa = %s"
        cls.query(query_update, tuple(valores))

        return cls.buscar_por_id(pessoa_id)

    @classmethod
    def listar(cls) -> list[dict]:
        query = "SELECT * FROM pessoa ORDER BY id_pessoa DESC"
        return cls.query(query) or []
