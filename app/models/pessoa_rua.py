import re

from infra.database import Database
from infra.erros import NotFoundError, ValidationError


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
        if not isinstance(dados, dict) or not dados:
            raise ValidationError(
                message="Body JSON inválido ou ausente.",
                action="Envie um JSON válido no corpo da requisição.",
            )

        descricao_fisica = dados.get("descricao_fisica")
        apelido = dados.get("apelido")
        cpf = dados.get("cpf_opcional")
        nome_civil = dados.get("nome_civil")

        if not apelido or not str(apelido).strip():
            raise ValidationError(
                message="Apelido inválido, esse dados é obrigatório.",
                action="Tente Novamente.",
            )

        if not descricao_fisica or not str(descricao_fisica).strip():
            raise ValidationError(
                message="Descrição física inválida, esse dados é obrigatório.",
                action="Tente Novamente.",
            )

        if cpf:
            cpf = re.sub(r"\D", "", str(cpf))

            if not cls.validar_cpf(cpf):
                raise ValidationError(
                    message="CPF inválido, não está de acordo com as normas formalizadas pela 'Receita Federal do Brasil'.",
                    action="Tente Novamente.",
                )

        if nome_civil is not None:
            nome_civil = str(nome_civil).strip()
            if not nome_civil:
                nome_civil = None

        query_insert = """
            INSERT INTO pessoa_rua(apelido, descricao_fisica, nome_civil, cpf_opcional)
            VALUES (%s, %s, %s, %s)
        """

        apelido = apelido.strip()
        descricao_fisica = descricao_fisica.strip()
        params_insert = (
            apelido,
            descricao_fisica,
            nome_civil,
            cpf,
        )
        cls.query(query_insert, params_insert)

        if cpf:
            query_select = "SELECT * FROM pessoa_rua WHERE cpf_opcional = %s LIMIT 1"
            params_select = (cpf,)

        else:
            query_select = """
                SELECT * FROM pessoa_rua
                WHERE apelido = %s
                ORDER BY id_pessoa_rua DESC
                LIMIT 1
            """
            params_select = (apelido,)

        rows = cls.query(query_select, params_select)

        if rows:
            return rows[0]
        else:
            raise NotFoundError(
                message="Usuário não encontrado.",
                action="Contate o suporte.",
            )

    @classmethod
    def buscar_por_id(cls, pessoa_id: int) -> dict | None:
        query = "SELECT * FROM pessoa_rua WHERE id_pessoa_rua = %s"
        params = (pessoa_id,)

        rows = cls.query(query, params)

        if rows:
            return rows[0]
        else:
            raise NotFoundError(
                message="Usuário não encontrado.", action="Contate o suporte."
            )

    @classmethod
    def buscar_por_apelido(cls, apelido: str) -> list[dict]:
        apelido = (apelido or "").strip()
        if not apelido:
            raise ValidationError(
                message="Parâmetro 'apelido' é obrigatório.",
                action="Informe um valor para pesquisa por apelido.",
            )

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
        if not isinstance(dados, dict) or not dados:
            raise ValidationError(
                message="Body JSON inválido ou ausente.",
                action="Envie um JSON válido no corpo da requisição.",
            )

        campos = []
        valores = []
        permitidos = ["apelido", "descricao_fisica", "nome_civil", "cpf_opcional"]

        dados_tratados = {}

        if "apelido" in dados:
            apelido = (dados.get("apelido") or "").strip()
            if not apelido:
                raise ValidationError(
                    message="Apelido inválido, esse dados é obrigatório.",
                    action="Tente Novamente.",
                )
            dados_tratados["apelido"] = apelido

        if "descricao_fisica" in dados:
            descricao_fisica = (dados.get("descricao_fisica") or "").strip()
            if not descricao_fisica:
                raise ValidationError(
                    message="Descrição física inválida, esse dados é obrigatório.",
                    action="Tente Novamente.",
                )
            dados_tratados["descricao_fisica"] = descricao_fisica

        if "nome_civil" in dados:
            nome_civil = dados.get("nome_civil")
            if nome_civil is None:
                dados_tratados["nome_civil"] = None

            else:
                nome_civil = str(nome_civil).strip()
                dados_tratados["nome_civil"] = nome_civil or None

        if "cpf_opcional" in dados:
            cpf = dados.get("cpf_opcional")
            if cpf is None or not str(cpf).strip():
                dados_tratados["cpf_opcional"] = None

            else:
                cpf = re.sub(r"\D", "", str(cpf)).strip()
                if not cls.validar_cpf(cpf):
                    raise ValidationError(
                        message="CPF inválido, não está de acordo com as normas formalizadas pela 'Receita Federal do Brasil'.",
                        action="Tente Novamente.",
                    )
                dados_tratados["cpf_opcional"] = cpf

        for campo in permitidos:
            if campo in dados_tratados:
                campos.append(f"{campo} = %s")
                valores.append(dados_tratados[campo])

        if not campos:
            return cls.buscar_por_id(pessoa_id)

        valores.append(pessoa_id)
        query_update = (
            f"UPDATE pessoa_rua SET {', '.join(campos)} WHERE id_pessoa_rua = %s"
        )
        params_update = tuple(valores)

        cls.query(query_update, params_update)

        return cls.buscar_por_id(pessoa_id)

    @classmethod
    def atualizar_risco(cls, pessoa_id: int, nivel_risco: str) -> dict | None:
        niveis_validos = {"baixo", "medio", "alto", "critico"}

        if nivel_risco not in niveis_validos:
            raise ValidationError(
                message=f"nivel_risco inválido: '{nivel_risco}'.",
                action=f"Use um dos valores válidos: {sorted(niveis_validos)}.",
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
        cpf_opcional: str | None = None,
    ) -> list[dict]:
        if nivel_risco and nivel_risco not in {"baixo", "medio", "alto", "critico"}:
            raise ValidationError(
                message="nivel_risco inválido.",
                action="Use um dos valores: baixo, medio, alto ou critico.",
            )

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

        if cpf_opcional:
            cpf_limpo = re.sub(r"\D", "", cpf_opcional)
            filtros.append("cpf_opcional = %s")
            valores.append(cpf_limpo)
        if filtros:
            query_base += " WHERE " + " AND ".join(filtros)

        query_base += " ORDER BY id_pessoa_rua DESC"

        rows = cls.query(query_base, tuple(valores))
        return rows or []

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        cpf = re.sub(r"\D", "", cpf or "")

        if len(cpf) != 11:
            return False

        # Rejeita sequências iguais
        if cpf == cpf[0] * 11:
            return False

        soma_digito_1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito_1 = (soma_digito_1 * 10) % 11

        if digito_1 == 10:
            digito_1 = 0

        soma_digito_2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito_2 = (soma_digito_2 * 10) % 11

        if digito_2 == 10:
            digito_2 = 0

        if digito_1 != int(cpf[9]):
            return False

        if digito_2 != int(cpf[10]):
            return False

        return True
