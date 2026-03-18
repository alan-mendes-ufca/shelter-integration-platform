"""
Model: Abrigo
=============

Gerencia o cadastro de abrigos e o contador de vagas disponíveis.

ATENÇÃO — comportamento de Database.query():
    SELECT  → retorna list[dict]
    INSERT  → retorna lastrowid (int)
    UPDATE  → retorna []  (NÃO retorna rowcount)

Por isso, toda verificação de "operação teve efeito?" é feita com
SELECT antes do UPDATE, nunca via rowcount.
"""

from infra.database import Database


class AbrigoModel(Database):
    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        """
        Cadastra um novo abrigo no sistema.

        Args:
            dados (dict):
                Obrigatórios: 'nome', 'endereco', 'capacidade_total'
                Opcionais:    'telefone'

        Returns:
            dict | None: Abrigo recém-criado.

        """
        nome = str(dados.get("nome") or "").strip()
        endereco = str(dados.get("endereco") or "").strip()
        capacidade_total = dados.get("capacidade_total")
        telefone = dados.get("telefone")

        if not nome:
            raise ValueError("O campo 'nome' é obrigatório.")
        if not endereco:
            raise ValueError("O campo 'endereco' é obrigatório.")
        if capacidade_total is None:
            raise ValueError("O campo 'capacidade_total' é obrigatório.")

        capacidade_total = int(capacidade_total)
        if capacidade_total <= 0:
            raise ValueError("'capacidade_total' deve ser um inteiro positivo.")

        capacidade = int(capacidade)

        lastrowid = cls.query(
            """
            INSERT INTO abrigo
                (nome, endereco, capacidade_total, vagas_disponiveis, telefone)
            VALUES
                (%s, %s, %s, %s, %s)
            """,
            (nome, endereco, capacidade, capacidade, dados.get("telefone")),
        )
        rows = cls.query("SELECT * FROM abrigo WHERE id_abrigo = %s", (lastrowid,))
        return rows[0] if rows else None
        return rows[0] if rows else None

    @classmethod
    def listar(cls, apenas_com_vagas: bool = False) -> list[dict]:
        """
        Lista todos os abrigos ativos.

        Args:
            apenas_com_vagas (bool): Se True, filtra apenas abrigos com
                                     vagas_disponiveis > 0 (usado em US07).

        Returns:
             list[dict]: Lista ordenada por nome.
        """
        if apenas_com_vagas:
            query = """
                SELECT * FROM abrigo
                WHERE ativo = TRUE AND vagas_disponiveis > 0
                ORDER BY nome
            """
        else:
query = "SELECT * FROM abrigo WHERE ativo = TRUE ORDER BY nome"

        rows = cls.query(query)
        return rows or []

    @classmethod
    def decrementar_vaga(cls, abrigo_id: int) -> bool:
        """
        """
        Decrementa vagas_disponiveis em 1.

        Faz SELECT antes do UPDATE porque query() não retorna rowcount.

        Args:
            abrigo_id (int): ID do abrigo.

        Returns:
            bool: True se decrementado, False se abrigo lotado ou inexistente.
        """
        rows = cls.query(
            """
            SELECT vagas_disponiveis FROM abrigo
            WHERE id_abrigo = %s AND ativo = TRUE
            """,
            (abrigo_id,),
        )
        if not rows or rows[0]["vagas_disponiveis"] <= 0:
            return False

        cls.query(
            """
            UPDATE abrigo
            SET vagas_disponiveis = vagas_disponiveis - 1
            WHERE id_abrigo = %s AND vagas_disponiveis > 0
            """,
            (abrigo_id,),
        )
        return True

    @classmethod
    def incrementar_vaga(cls, abrigo_id: int) -> bool:
        """
        """
        Incrementa vagas_disponiveis em 1.

        O WHERE vagas_disponiveis < capacidade_total complementa o
        CHECK constraint do banco, impedindo ultrapassar o limite.

        Raises:
            ValueError: Se a pessoa já estiver acolhida em outro abrigo.
            RuntimeError: Se o abrigo não tiver vagas disponíveis.
        """
        # 1. Pessoa já acolhida em algum abrigo?
        vaga_ativa = cls.query(
            "SELECT id_vaga FROM vaga WHERE pessoa_id = %s AND status = 'ocupada'",
            (pessoa_id,),
        )
        if vaga_ativa:
            raise ValueError(
                "A pessoa já está acolhida em um abrigo. "
                "Registre a saída antes de uma nova entrada."
            )

        # 2. Tenta decrementar — já verifica disponibilidade internamente
        if not AbrigoModel.decrementar_vaga(abrigo_id):
            raise RuntimeError("O abrigo não possui vagas disponíveis no momento.")

        # 3. Insere o registro de ocupação
        query_insert = """
            INSERT INTO vaga (pessoa_id, abrigo_id, status)
            VALUES (%s, %s, 'ocupada')
        """
        vaga_id = cls.query(query_insert, (pessoa_id, abrigo_id))

        return cls._buscar_por_id(vaga_id)

    @classmethod
    def registrar_saida(cls, vaga_id: int) -> dict | None:
        """
        Registra a saída da pessoa do abrigo e libera a vaga (US09).

        Returns:
            bool: True sempre (constraint do banco protege o limite superior).
        """
        # 1. Busca a vaga — diferencia "não existe" de "já liberada"
        vaga = cls._buscar_por_id(vaga_id)
        if not vaga:
            return None  # controller → 404

        if vaga["status"] == "liberada":
            return None  # controller → 409

        # 2. Atualiza status e preenche saida_em
        cls.query(
            """
            UPDATE abrigo
            SET vagas_disponiveis = vagas_disponiveis + 1
            WHERE id_abrigo = %s AND vagas_disponiveis < capacidade_total
            """,
            (abrigo_id,),
        )
        return True
