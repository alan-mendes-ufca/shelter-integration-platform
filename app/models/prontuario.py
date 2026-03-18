from infra.database import Database


class ProntuarioModel(Database):
    """
    Model da tabela `prontuario`.
    Gerencia o histórico de atendimento das pessoas em situação de rua.
    """

    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        id_pessoa_rua = dados.get("id_pessoa_rua")
        id_consentimento = dados.get("id_consentimento")
        id_profissional = dados.get("id_profissional")
        resumo_historico = dados.get("resumo_historico", "")

        if not id_pessoa_rua or not id_consentimento or not id_profissional:
            raise ValueError(
                "Os campos id_pessoa_rua, id_consentimento e id_profissional são obrigatórios."
            )

        query_insert = """
            INSERT INTO prontuario (id_pessoa_rua, id_consentimento, id_profissional, resumo_historico)
            VALUES (%s, %s, %s, %s)
        """
        params_insert = (
            id_pessoa_rua,
            id_consentimento,
            id_profissional,
            resumo_historico,
        )

        cls.query(query_insert, params_insert)

        return cls.buscar_por_id(id_pessoa_rua)

    @classmethod
    def buscar_por_id(cls, id_pessoa_rua: int) -> dict | None:
        query_select = """
            SELECT 
                p.id_pessoa_rua, p.id_consentimento, p.id_profissional, 
                p.data_criacao, p.resumo_historico,
                pr.apelido, pr.nivel_risco as grau_vulnerabilidade
            FROM prontuario p
            INNER JOIN pessoa_rua pr ON p.id_pessoa_rua = pr.id_pessoa_rua
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

        id_consentimento_atual = prontuario_atual["id_consentimento"]

        # --- INÍCIO DO MOCK DE CONSENTIMENTO ---
        # Quando o Membro 2 terminar, apague este mock e volte com o SELECT no banco

        # Vamos fingir que o ID 999 significa "Consentimento Revogado"
        if id_consentimento_atual == 999:
            raise PermissionError(
                "Edição bloqueada (MOCK): O morador de rua revogou o consentimento de uso de dados."
            )

        # Se for qualquer outro ID, o mock deixa a execução continuar normalmente...
        # --- FIM DO MOCK ---

        # 2. Atualização na tabela PRONTUÁRIO
        campos_prontuario = []
        valores_prontuario = []

        if "resumo_historico" in dados:
            campos_prontuario.append("resumo_historico = %s")
            valores_prontuario.append(dados["resumo_historico"])

        if "id_profissional" in dados:
            campos_prontuario.append("id_profissional = %s")
            valores_prontuario.append(dados["id_profissional"])

        if "id_consentimento" in dados:
            campos_prontuario.append("id_consentimento = %s")
            valores_prontuario.append(dados["id_consentimento"])

        if campos_prontuario:
            valores_prontuario.append(id_pessoa_rua)
            query_prontuario = f"UPDATE prontuario SET {', '.join(campos_prontuario)} WHERE id_pessoa_rua = %s"
            cls.query(query_prontuario, tuple(valores_prontuario))

        # 3. Atualização na tabela PESSOA_RUA (Grau de Vulnerabilidade / nivel_risco)
        if "grau_vulnerabilidade" in dados:
            nivel_risco = dados["grau_vulnerabilidade"]
            niveis_validos = {"baixo", "medio", "alto", "critico"}

            if nivel_risco not in niveis_validos:
                raise ValueError(
                    f"grau_vulnerabilidade inválido. Valores aceitos: {sorted(niveis_validos)}"
                )

            query_risco = (
                "UPDATE pessoa_rua SET nivel_risco = %s WHERE id_pessoa_rua = %s"
            )
            cls.query(query_risco, (nivel_risco, id_pessoa_rua))

        return cls.buscar_por_id(id_pessoa_rua)
