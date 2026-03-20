from infra.database import Database
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

    @staticmethod
    def _validar_filtros_listagem(
        filtros: dict,
    ) -> tuple[int | None, str | None, str | None]:
        id_abrigo_raw = str((filtros or {}).get("id_abrigo", "")).strip()
        data_inicio = str((filtros or {}).get("data_inicio", "")).strip() or None
        data_fim = str((filtros or {}).get("data_fim", "")).strip() or None

        id_abrigo = None
        if id_abrigo_raw:
            try:
                id_abrigo = int(id_abrigo_raw)
            except ValueError as err:
                raise ValidationError(
                    message="O parâmetro 'id_abrigo' deve ser numérico.",
                    action="Informe um id_abrigo inteiro e válido.",
                ) from err

        return id_abrigo, data_inicio, data_fim

    @classmethod
    def registrar(cls, data: dict) -> dict | None:
        cls._validar_dados_registro(data)

        pessoa_rua = PessoaRuaModel.buscar_por_id(int(data["id_pessoa_rua"]))
        profissional = ProfissionalModel.buscar_por_id(int(data["id_profissional"]))
        abrigo_id = cls._validar_abrigo(data.get("id_abrigo"))

        if not pessoa_rua:
            raise NotFoundError(
                message="Pessoa em situação de rua não encontrada.",
                action="Verifique o 'id_pessoa_rua' informado.",
            )

        if not profissional:
            raise NotFoundError(
                message="Profissional não encontrado.",
                action="Verifique o 'id_profissional' informado.",
            )

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
    def listar_filtrados(cls, filtros: dict) -> list[dict]:
        id_abrigo, data_inicio, data_fim = cls._validar_filtros_listagem(filtros)

        conditions = []
        params = []

        if id_abrigo is not None:
            cls._validar_abrigo(id_abrigo)
            conditions.append("id_abrigo = %s")
            params.append(id_abrigo)

        if data_inicio:
            conditions.append("realizado_em >= %s")
            params.append(data_inicio)

        if data_fim:
            conditions.append("realizado_em <= CONCAT(%s, ' 23:59:59')")
            params.append(data_fim)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        query = f"SELECT * FROM atendimento {where} ORDER BY realizado_em DESC;"

        result = cls.query(query, params if params else None)
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
