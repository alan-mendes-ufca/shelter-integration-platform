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

    @staticmethod
    def _validar_apelido_obrigatorio(apelido: object) -> str:
        if not apelido or not str(apelido).strip():
            raise ValidationError(
                message="Apelido inválido, esse dados é obrigatório.",
                action="Tente Novamente.",
            )
        return str(apelido).strip()

    @staticmethod
    def _validar_descricao_fisica_obrigatoria(descricao_fisica: object) -> str:
        if not descricao_fisica or not str(descricao_fisica).strip():
            raise ValidationError(
                message="Descrição física inválida, esse dados é obrigatório.",
                action="Tente Novamente.",
            )
        return str(descricao_fisica).strip()

    @staticmethod
    def _normalizar_nome_civil(nome_civil: object) -> str | None:
        if nome_civil is not None:
            nome_civil = str(nome_civil).strip()
            if not nome_civil:
                return None
            return nome_civil
        return None

    @classmethod
    def _validar_cpf_criacao(cls, cpf: object) -> str | None:
        if cpf:
            cpf = re.sub(r"\D", "", str(cpf))
            if not cls.validar_cpf(cpf):
                raise ValidationError(
                    message="CPF inválido, não está de acordo com as normas formalizadas pela 'Receita Federal do Brasil'.",
                    action="Tente Novamente.",
                )
        return cpf

    @classmethod
    def _validar_cpf_atualizacao(cls, cpf: object) -> str | None:
        if cpf is None or not str(cpf).strip():
            return None

        cpf = re.sub(r"\D", "", str(cpf)).strip()
        if not cls.validar_cpf(cpf):
            raise ValidationError(
                message="CPF inválido, não está de acordo com as normas formalizadas pela 'Receita Federal do Brasil'.",
                action="Tente Novamente.",
            )
        return cpf

    @staticmethod
    def _validar_nivel_risco_atualizacao(nivel_risco: str) -> str:
        niveis_validos = {"baixo", "medio", "alto", "critico"}
        if nivel_risco not in niveis_validos:
            raise ValidationError(
                message=f"nivel_risco inválido: '{nivel_risco}'.",
                action=f"Use um dos valores válidos: {sorted(niveis_validos)}.",
            )
        return nivel_risco

    @staticmethod
    def _validar_nivel_risco_filtro(nivel_risco: str | None) -> None:
        if nivel_risco and nivel_risco not in {"baixo", "medio", "alto", "critico"}:
            raise ValidationError(
                message="nivel_risco inválido.",
                action="Use um dos valores: baixo, medio, alto ou critico.",
            )

    @staticmethod
    def _validar_apelido_busca(apelido: str) -> str:
        apelido = (apelido or "").strip()
        if not apelido:
            raise ValidationError(
                message="Parâmetro 'apelido' é obrigatório.",
                action="Informe um valor para pesquisa por apelido.",
            )
        return apelido

    @classmethod
    def criar(cls, dados: dict) -> dict | None:

        descricao_fisica = dados.get("descricao_fisica")
        apelido = dados.get("apelido")
        cpf = dados.get("cpf_opcional")
        nome_civil = dados.get("nome_civil")

        apelido = cls._validar_apelido_obrigatorio(apelido)
        descricao_fisica = cls._validar_descricao_fisica_obrigatoria(descricao_fisica)
        cpf = cls._validar_cpf_criacao(cpf)
        nome_civil = cls._normalizar_nome_civil(nome_civil)

        query_insert = """
            INSERT INTO pessoa_rua(apelido, descricao_fisica, nome_civil, cpf_opcional)
            VALUES (%s, %s, %s, %s)
        """

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
        apelido = cls._validar_apelido_busca(apelido)

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

        dados_tratados = {}

        if "apelido" in dados:
            dados_tratados["apelido"] = cls._validar_apelido_obrigatorio(
                dados.get("apelido")
            )

        if "descricao_fisica" in dados:
            dados_tratados["descricao_fisica"] = (
                cls._validar_descricao_fisica_obrigatoria(dados.get("descricao_fisica"))
            )

        if "nome_civil" in dados:
            dados_tratados["nome_civil"] = cls._normalizar_nome_civil(
                dados.get("nome_civil")
            )

        if "cpf_opcional" in dados:
            dados_tratados["cpf_opcional"] = cls._validar_cpf_atualizacao(
                dados.get("cpf_opcional")
            )

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
        nivel_risco = cls._validar_nivel_risco_atualizacao(nivel_risco)

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
        cls._validar_nivel_risco_filtro(nivel_risco)

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
