"""
Model: Vaga
===========

Gerencia as ocupações individuais de vagas em abrigos.

Regras de negócio:
    - Uma pessoa não pode estar em dois abrigos simultaneamente.
    - Entrada só é possível se o abrigo tiver vagas disponíveis.
    - Saída só é possível se a vaga estiver com status 'ocupada'.

Débito técnico registrado:
    Entrada deveria ser atômica: decrementar + inserir em um único COMMIT.
    Por enquanto as duas operações ocorrem em sequência. Se o INSERT falhar
    após o decremento, o contador ficará inconsistente. Resolver quando
    Database.query() suportar transações explícitas.
"""

from infra.database import Database
from app.models.abrigo import AbrigoModel


class VagaModel(Database):
    @classmethod
    def registrar_entrada(cls, pessoa_id: int, abrigo_id: int) -> dict | None:
        """
        Registra a entrada de uma pessoa em um abrigo (US08).

        Sequência:
            1. Verifica se a pessoa já está alocada em algum abrigo.
            2. Decrementa o contador do abrigo (False = sem vagas).
            3. Insere o registro com status 'ocupada'.

        Args:
            pessoa_id (int): ID da pessoa entrando no abrigo.
            abrigo_id (int): ID do abrigo.

        Returns:
            dict | None: Registro da vaga criada.

        Raises:
            ValueError: Se a pessoa já estiver alocada ou o abrigo estiver lotado.
        """
        # 1 — Pessoa já está ocupando alguma vaga?
        ocupada = cls.query(
            "SELECT id_vaga FROM vaga WHERE pessoa_id = %s AND status = 'ocupada'",
            (pessoa_id,),
        )
        if ocupada:
            raise ValueError(
                "Pessoa já está alocada em um abrigo. "
                "Registre a saída antes de fazer um novo encaminhamento."
            )

        # 2 — Tenta decrementar (protege contra overbooking)
        if not AbrigoModel.decrementar_vaga(abrigo_id):
            raise ValueError(
                "Abrigo sem vagas disponíveis. "
                "Consulte outro abrigo ou aguarde uma liberação."
            )

        # 3 — Registra a entrada
        lastrowid = cls.query(
            """
            INSERT INTO vaga (pessoa_id, abrigo_id, status, entrada_em)
            VALUES (%s, %s, 'ocupada', NOW())
            """,
            (pessoa_id, abrigo_id),
        )
        rows = cls.query("SELECT * FROM vaga WHERE id_vaga = %s", (lastrowid,))
        return rows[0] if rows else None

    @classmethod
    def registrar_saida(cls, vaga_id: int) -> dict | None:
        """
        Registra a saída da pessoa do abrigo e libera a vaga (US09).

        Sequência:
            1. Busca e valida que a vaga existe e está 'ocupada'.
            2. Atualiza status para 'liberada' e preenche saida_em.
            3. Incrementa o contador de vagas do abrigo.

        Args:
            vaga_id (int): ID do registro de ocupação.

        Returns:
            dict | None: Vaga atualizada.
                         None se não encontrada  → controller retorna 404.
                         None se já liberada     → controller retorna 409.
        """
        rows = cls.query("SELECT * FROM vaga WHERE id_vaga = %s", (vaga_id,))
        if not rows:
            return None  # 404

        vaga = rows[0]

        if vaga["status"] != "ocupada":
            return None  # 409

        cls.query(
            """
            UPDATE vaga
            SET status = 'liberada', saida_em = NOW()
            WHERE id_vaga = %s AND status = 'ocupada'
            """,
            (vaga_id,),
        )

        AbrigoModel.incrementar_vaga(vaga["abrigo_id"])

        rows = cls.query("SELECT * FROM vaga WHERE id_vaga = %s", (vaga_id,))
        return rows[0] if rows else None

    @classmethod
    def buscar_por_id(cls, vaga_id: int) -> dict | None:
        """
        Retorna uma vaga pelo ID.

        Args:
            vaga_id (int): ID da vaga.

        Returns:
            dict | None: Dados da vaga ou None se não existir.
        """
        rows = cls.query("SELECT * FROM vaga WHERE id_vaga = %s", (vaga_id,))
        return rows[0] if rows else None

    @classmethod
    def listar_por_abrigo(cls, abrigo_id: int) -> list[dict]:
        """
        Lista todas as ocupações de um abrigo (ativas e históricas).

        JOIN com pessoa_rua para trazer apelido, evitando N+1 queries.

        Args:
            abrigo_id (int): ID do abrigo.

        Returns:
            list[dict]: Lista ordenada por entrada_em DESC.
        """
        rows = cls.query(
            """
            SELECT v.*, p.apelido AS pessoa_apelido
            FROM vaga v
            JOIN pessoa_rua p ON p.id_pessoa_rua = v.pessoa_id
            WHERE v.abrigo_id = %s
            ORDER BY v.entrada_em DESC
            """,
            (abrigo_id,),
        )
        return rows or []

    @classmethod
    def listar_por_pessoa(cls, pessoa_id: int) -> list[dict]:
        """
        Lista o histórico de abrigos de uma pessoa.

        Args:
            pessoa_id (int): ID da pessoa.

        Returns:
            list[dict]: Lista com nome do abrigo, ordenada por entrada_em DESC.
        """
        rows = cls.query(
            """
            SELECT v.*, a.nome AS abrigo_nome, a.endereco AS abrigo_endereco
            FROM vaga v
            JOIN abrigo a ON a.id_abrigo = v.abrigo_id
            WHERE v.pessoa_id = %s
            ORDER BY v.entrada_em DESC
            """,
            (pessoa_id,),
        )
        return rows or []
