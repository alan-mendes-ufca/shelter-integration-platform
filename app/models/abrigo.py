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

        Regra de negócio:
            vagas_disponiveis começa igual a capacidade_total.
            O frontend nunca define vagas_disponiveis diretamente.
        """
        nome = (dados.get("nome") or "").strip()
        endereco = (dados.get("endereco") or "").strip()
        capacidade = dados.get("capacidade_total")

        if not nome:
            raise ValueError("nome é obrigatório.")
        if not endereco:
            raise ValueError("endereco é obrigatório.")
        if capacidade is None or int(capacidade) <= 0:
            raise ValueError("capacidade_total deve ser um inteiro positivo.")

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
    def buscar_por_id(cls, abrigo_id: int) -> dict | None:
        """
        Retorna um abrigo pelo ID.

        Args:
            abrigo_id (int): ID do abrigo.

        Returns:
            dict | None: Dados do abrigo ou None se não existir.
        """
        rows = cls.query("SELECT * FROM abrigo WHERE id_abrigo = %s", (abrigo_id,))
        return rows[0] if rows else None

    @classmethod
    def decrementar_vaga(cls, abrigo_id: int) -> bool:
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
        Incrementa vagas_disponiveis em 1.

        O WHERE vagas_disponiveis < capacidade_total complementa o
        CHECK constraint do banco, impedindo ultrapassar o limite.

        Args:
            abrigo_id (int): ID do abrigo.

        Returns:
            bool: True sempre (constraint do banco protege o limite superior).
        """
        cls.query(
            """
            UPDATE abrigo
            SET vagas_disponiveis = vagas_disponiveis + 1
            WHERE id_abrigo = %s AND vagas_disponiveis < capacidade_total
            """,
            (abrigo_id,),
        )
        return True
