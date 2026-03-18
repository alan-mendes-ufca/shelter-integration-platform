from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo
from infra.erros import NotFoundError, ValidationError
from .abrigo import AbrigoModel
from .pessoa_rua import PessoaRuaModel
from .profissional import ProfissionalModel


class AtendimentoModel(Database):
    TIPOS_ATENDIMENTO_VALIDOS = {
        "escuta",
        "alimentacao",
        "banho",
        "saude",
        "juridico",
        "outro",
    }

    @classmethod
    def _validar_dados_registro(cls, data: dict) -> None:
        required_fields = {"id_pessoa_rua", "id_profissional", "id_abrigo", "tipo"}
        optional_fields = {"observacoes"}
        allowed_fields = required_fields | optional_fields

        if not data:
            raise ValidationError(
                message="Campos obrigatórios faltando ou extras presentes.",
                action="Verifique se 'id_pessoa_rua', 'id_profissional', 'id_abrigo' e 'tipo' estão presentes e sem campos adicionais.",
            )

        data_keys = set(data.keys())
        if not required_fields.issubset(data_keys) or not data_keys.issubset(
            allowed_fields
        ):
            raise ValidationError(
                message="Campos obrigatórios faltando ou extras presentes.",
                action="Verifique se 'id_pessoa_rua', 'id_profissional', 'id_abrigo' e 'tipo' estão presentes e sem campos adicionais.",
            )

        if data["tipo"] not in cls.TIPOS_ATENDIMENTO_VALIDOS:
            cls._raise_tipo_invalido()

        cls._validar_abrigo(data.get("id_abrigo"))

    @classmethod
    def _validar_dados_atualizacao(cls, dados: dict) -> set[str]:
        if not dados:
            raise ValidationError(
                message="Body JSON inválido ou ausente.",
                action="Envie ao menos um campo para atualização.",
            )

        campos_permitidos = {"tipo", "id_abrigo", "observacoes"}
        campos_invalidos = set(dados.keys()) - campos_permitidos
        if campos_invalidos:
            raise ValidationError(
                message="Body contém campos não permitidos para atualização.",
                action="Utilize somente os campos: 'tipo', 'id_abrigo', 'observacoes'.",
            )

        if "tipo" in dados and dados["tipo"] not in cls.TIPOS_ATENDIMENTO_VALIDOS:
            cls._raise_tipo_invalido()

        if "id_abrigo" in dados:
            cls._validar_abrigo(dados.get("id_abrigo"))

        return campos_permitidos

    @staticmethod
    def _raise_tipo_invalido() -> None:
        raise ValidationError(
            message="Campo de 'tipo' preenchido com opção inválida.",
            action="Utilize somente uma das opção a seguir: 'escuta', 'alimentacao', 'banho', 'saude', 'juridico', 'outro'.",
        )

    @staticmethod
    def _validar_abrigo(id_abrigo: object) -> int:
        try:
            abrigo_id = int(id_abrigo)
        except (TypeError, ValueError) as err:
            raise ValidationError(
                message="O campo 'id_abrigo' deve ser um inteiro válido.",
                action="Informe um id_abrigo existente e numérico.",
            ) from err

        abrigo = AbrigoModel.buscar_por_id(abrigo_id)
        if not abrigo:
            raise ValidationError(
                message="Abrigo não encontrado.",
                action="Informe um id_abrigo válido e ativo.",
            )

        return abrigo_id

    @classmethod
    def _buscar_atendimento_valido(cls, atendimento_id: int) -> dict:
        atendimento_atual = cls.buscar_por_id(atendimento_id)
        if not atendimento_atual:
            raise NotFoundError(
                message="Atendimento não encontrado.",
                action="Verifique o ID informado.",
            )
        return atendimento_atual

    @classmethod
    def registrar(cls, data: dict) -> dict | None:
        cls._validar_dados_registro(data)

        pessoa_rua = PessoaRuaModel.buscar_por_id(int(data["id_pessoa_rua"]))
        profissional = ProfissionalModel.buscar_por_id(int(data["id_profissional"]))
        abrigo_id = cls._validar_abrigo(data.get("id_abrigo"))

        query = """
            INSERT INTO atendimento
                (id_pessoa_rua, id_profissional, id_abrigo, tipo, observacoes)
            VALUES
                (%s, %s, %s, %s, %s);
        """
        params = (
            pessoa_rua["id_pessoa_rua"],
            profissional["id_profissional"],
            abrigo_id,
            data["tipo"],
            data.get("observacoes", "Sem observações"),
        )

        lastrowid = cls.query(query, params)
        result = cls.query(
            "SELECT * FROM atendimento WHERE id_atendimento = %s;", (lastrowid,)
        )
        return result[0] if result else None

    @classmethod
    def buscar_por_id(cls, atendimento_id: int) -> dict | None:
        query = "SELECT * FROM atendimento WHERE id_atendimento = %s;"
        result = cls.query(query, (atendimento_id,))
        return result[0] if result else None

    @classmethod
    def listar_por_pessoa(cls, pessoa_id: int) -> list[dict]:
        query = """
            SELECT
                at.*,
                pe.nome AS profissional_nome
            FROM atendimento at
            LEFT JOIN profissional pr
                ON at.id_profissional = pr.id_profissional
            LEFT JOIN pessoa pe
                ON pr.id_pessoa = pe.id_pessoa
            WHERE at.id_pessoa_rua = %s
            ORDER BY at.realizado_em DESC;
        """
        result = cls.query(query, (pessoa_id,))
        return result or []

    @classmethod
    def listar_por_abrigo_e_periodo(
        cls, id_abrigo: int, data_inicio: str, data_fim: str
    ) -> list[dict]:
        abrigo_id = cls._validar_abrigo(id_abrigo)
        query = """
            SELECT *
            FROM atendimento
            WHERE id_abrigo = %s
              AND realizado_em BETWEEN %s AND CONCAT(%s, ' 23:59:59')
            ORDER BY realizado_em DESC;
        """
        params = (abrigo_id, data_inicio, data_fim)
        result = cls.query(query, params)
        return result or []

    @classmethod
    def atualizar(cls, atendimento_id: int, dados: dict) -> dict | None:
        cls._validar_dados_atualizacao(dados)
        atendimento_atual = cls._buscar_atendimento_valido(atendimento_id)

        atendimento_atualizado = {**atendimento_atual, **dados}
        params = (
            atendimento_atualizado["tipo"],
            atendimento_atualizado["id_abrigo"],
            atendimento_atualizado["observacoes"],
            atendimento_id,
        )

        query = """
            UPDATE atendimento
            SET tipo = %s, id_abrigo = %s, observacoes = %s
            WHERE id_atendimento = %s;
        """

        cls.query(query, params)

        return cls.buscar_por_id(atendimento_id)

    @classmethod
    def deletar(cls, atendimento_id: int) -> bool:

        atendimento = cls.buscar_por_id(atendimento_id)
        if not atendimento:
            return False

        query = "DELETE FROM atendimento WHERE id_atendimento = %s;"
        cls.query(query, (atendimento_id,))
        return True
