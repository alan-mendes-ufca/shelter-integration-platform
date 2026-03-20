from infra.database import Database
from infra.erros import ValidationError


class ProntuarioModel(Database):
    """
    Model da tabela `prontuario`.
    Gerencia o histórico de atendimento das pessoas em situação de rua.
    """

    @staticmethod
    def _validar_ids_obrigatorios_criacao(
        id_pessoa_rua: object, id_profissional: object
    ) -> None:
        if not id_pessoa_rua or not id_profissional:
            raise ValidationError(
                message="Os campos id_pessoa_rua e id_profissional são obrigatórios.",
                action="Envie todos os campos obrigatórios para criação do prontuário.",
            )

    @staticmethod
    def _validar_consentimento_ativo(ativo: bool) -> None:
        # Agora recebe diretamente o valor booleano
        if not ativo:
            raise ValidationError(
                message="Edição bloqueada: o consentimento de uso de dados foi revogado.",
                action="Solicite novo consentimento antes de editar o prontuário.",
            )

    @staticmethod
    def _validar_grau_vulnerabilidade(nivel_risco: str) -> str:
        niveis_validos = {"baixo", "medio", "alto", "critico"}

        if nivel_risco not in niveis_validos:
            raise ValidationError(
                message="grau_vulnerabilidade inválido.",
                action=f"Use um dos valores aceitos: {sorted(niveis_validos)}.",
            )

        return nivel_risco

    @classmethod
    def _validar_pessoa_sem_prontuario(cls, id_pessoa_rua: object) -> None:
        if cls.buscar_por_id(id_pessoa_rua):
            raise ValidationError(
                message="A pessoa informada já possui prontuário cadastrado.",
                action="Utilize o endpoint de atualização para alterar o prontuário existente.",
            )

    @classmethod
    def criar(cls, dados: dict) -> dict | None:

        id_pessoa_rua = dados.get("id_pessoa_rua")
        id_profissional = dados.get("id_profissional")
        resumo_historico = dados.get("resumo_historico", "")

        cls._validar_ids_obrigatorios_criacao(
            id_pessoa_rua,
            id_profissional,
        )
        cls._validar_pessoa_sem_prontuario(id_pessoa_rua)

        query_insert = """
            INSERT INTO prontuario (id_pessoa_rua, id_profissional, resumo_historico)
            VALUES (%s, %s, %s)
        """
        params_insert = (
            id_pessoa_rua,
            id_profissional,
            resumo_historico,
        )

        cls.query(query_insert, params_insert)

        return cls.buscar_por_id(id_pessoa_rua)

    @classmethod
    def buscar_por_id(cls, id_pessoa_rua: int) -> dict | None:
        # ATUALIZAÇÃO: Adicionado o INNER JOIN com consentimento para trazer o campo 'ativo'
        query_select = """
            SELECT
                p.id_pessoa_rua, p.id_profissional,
                p.data_criacao, p.resumo_historico,
                pr.apelido, pr.nivel_risco as grau_vulnerabilidade,
                c.ativo
            FROM prontuario p
            INNER JOIN pessoa_rua pr ON p.id_pessoa_rua = pr.id_pessoa_rua
            INNER JOIN consentimento c ON p.id_pessoa_rua = c.id_pessoa_rua
            WHERE p.id_pessoa_rua = %s
        """
        rows = cls.query(query_select, (id_pessoa_rua,))

        if rows:
            return rows[0]
        return None

    @classmethod
    def atualizar(cls, id_pessoa_rua: int, dados: dict) -> dict | None:

        prontuario_atual = cls.buscar_por_id(id_pessoa_rua)
        if not prontuario_atual:
            return None

        # Agora pega o status 'ativo' real vindo do banco de dados
        ativo_atual = prontuario_atual.get("ativo")
        cls._validar_consentimento_ativo(ativo_atual)

        campos_prontuario = []
        valores_prontuario = []

        if "resumo_historico" in dados:
            campos_prontuario.append("resumo_historico = %s")
            valores_prontuario.append(dados["resumo_historico"])

        if "id_profissional" in dados:
            campos_prontuario.append("id_profissional = %s")
            valores_prontuario.append(dados["id_profissional"])

        # O bloco de código que tentava salvar "id_consentimento" foi deletado daqui!

        if campos_prontuario:
            valores_prontuario.append(id_pessoa_rua)
            query_prontuario = f"UPDATE prontuario SET {', '.join(campos_prontuario)} WHERE id_pessoa_rua = %s"
            cls.query(query_prontuario, tuple(valores_prontuario))

        if "grau_vulnerabilidade" in dados:
            nivel_risco = cls._validar_grau_vulnerabilidade(
                dados["grau_vulnerabilidade"]
            )

            query_risco = (
                "UPDATE pessoa_rua SET nivel_risco = %s WHERE id_pessoa_rua = %s"
            )
            cls.query(query_risco, (nivel_risco, id_pessoa_rua))

        return cls.buscar_por_id(id_pessoa_rua)
