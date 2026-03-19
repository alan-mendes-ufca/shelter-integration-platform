"""
Model: Abrigo + VagaCama + Estadia
====================================

Estrutura alinhada ao DER original:

  AbrigoModel   → cadastro e contagem de vagas do abrigo
  VagaCamaModel → inventário de camas numeradas por abrigo
  EstadiaModel  → ocupação de uma cama específica por uma pessoa

Fluxo de entrada:
  EstadiaModel.registrar_entrada(pessoa_id, abrigo_id)
    → VagaCamaModel.alocar_cama(abrigo_id)       — encontra e ocupa cama livre
    → AbrigoModel.decrementar_vaga(abrigo_id)     — atualiza o contador
    → INSERT em estadia

Fluxo de saída:
  EstadiaModel.registrar_saida(pessoa_id, motivo_saida)
    → UPDATE estadia SET data_saida=NOW()
    → VagaCamaModel.liberar_cama(numero_cama, abrigo_id)
    → AbrigoModel.incrementar_vaga(abrigo_id)

DÉBITO TÉCNICO: múltiplas queries em sequência sem transação atômica.
Implementar suporte a transações no Database.query() quando possível.
"""

from infra.database import Database
from infra.erros import ValidationError


class AbrigoModel(Database):
    """
    Gerencia o cadastro de abrigos e o contador de vagas disponíveis.
    """

    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        """
        Cadastra um novo abrigo e popula automaticamente suas camas em vaga_cama.

        Args:
            dados (dict): Obrigatórios: 'nome', 'endereco', 'capacidade_total'
                          Opcionais: 'telefone'

        Returns:
            dict | None: Abrigo recém-criado.
        """
        if not isinstance(dados, dict) or not dados:
            raise ValidationError(
                message="Body JSON inválido ou ausente.",
                action="Envie um JSON válido no corpo da requisição.",
            )

        nome = str(dados.get("nome") or "").strip()
        endereco = str(dados.get("endereco") or "").strip()
        capacidade_total = dados.get("capacidade_total")
        telefone = dados.get("telefone")

        if not nome:
            raise ValidationError(
                message="O campo 'nome' é obrigatório.",
                action="Informe um nome válido para o abrigo.",
            )
        if not endereco:
            raise ValidationError(
                message="O campo 'endereco' é obrigatório.",
                action="Informe um endereço válido para o abrigo.",
            )
        if capacidade_total is None:
            raise ValidationError(
                message="O campo 'capacidade_total' é obrigatório.",
                action="Informe a capacidade total do abrigo.",
            )

        try:
            capacidade_total = int(capacidade_total)
        except (TypeError, ValueError) as err:
            raise ValidationError(
                message="'capacidade_total' deve ser numérico.",
                action="Informe um inteiro positivo para 'capacidade_total'.",
            ) from err

        if capacidade_total <= 0:
            raise ValidationError(
                message="'capacidade_total' deve ser um inteiro positivo.",
                action="Informe um valor maior que zero para 'capacidade_total'.",
            )

        if telefone:
            telefone = str(telefone).strip() or None

        abrigo_id = cls.query(
            """
            INSERT INTO abrigo (nome, endereco, capacidade_total, vagas_disponiveis, telefone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (nome, endereco, capacidade_total, capacidade_total, telefone),
        )

        # Popula vaga_cama com todas as camas do abrigo recém-criado
        VagaCamaModel.popular_camas(abrigo_id, capacidade_total)

        rows = cls.query("SELECT * FROM abrigo WHERE id_abrigo = %s", (abrigo_id,))
        return rows[0] if rows else None

    @classmethod
    def listar(cls, apenas_com_vagas: bool = False) -> list[dict]:
        """
        Lista todos os abrigos ativos, ordenados por nome.

        Args:
            apenas_com_vagas (bool): Se True, filtra apenas abrigos com vagas > 0.
        """
        if apenas_com_vagas:
            query = """
                SELECT * FROM abrigo
                WHERE ativo = TRUE AND vagas_disponiveis > 0
                ORDER BY nome
            """
        else:
            query = "SELECT * FROM abrigo WHERE ativo = TRUE ORDER BY nome"

        return cls.query(query) or []

    @classmethod
    def buscar_por_id(cls, abrigo_id: int) -> dict | None:
        """Busca um abrigo ativo pelo ID."""
        rows = cls.query(
            "SELECT * FROM abrigo WHERE id_abrigo = %s AND ativo = TRUE", (abrigo_id,)
        )
        return rows[0] if rows else None

    @classmethod
    def decrementar_vaga(cls, abrigo_id: int) -> bool:
        """
        Decrementa vagas_disponiveis em 1. Retorna False se não houver vagas.
        """
        abrigo = cls.query(
            "SELECT vagas_disponiveis FROM abrigo WHERE id_abrigo = %s", (abrigo_id,)
        )
        if not abrigo or abrigo[0]["vagas_disponiveis"] <= 0:
            return False

        cls.query(
            """
            UPDATE abrigo SET vagas_disponiveis = vagas_disponiveis - 1
            WHERE id_abrigo = %s AND vagas_disponiveis > 0
            """,
            (abrigo_id,),
        )
        return True

    @classmethod
    def incrementar_vaga(cls, abrigo_id: int) -> bool:
        """
        Incrementa vagas_disponiveis em 1, respeitando a capacidade total.
        """
        cls.query(
            """
            UPDATE abrigo SET vagas_disponiveis = vagas_disponiveis + 1
            WHERE id_abrigo = %s AND vagas_disponiveis < capacidade_total
            """,
            (abrigo_id,),
        )
        return True


class VagaCamaModel(Database):
    """
    Gerencia o inventário de camas numeradas por abrigo.

    Cada cama tem número único dentro do abrigo e status: 'livre' ou 'ocupada'.
    """

    @classmethod
    def popular_camas(cls, abrigo_id: int, capacidade_total: int) -> None:
        """
        Cria todas as camas de um abrigo recém-cadastrado (1 até capacidade_total).
        Chamado automaticamente por AbrigoModel.criar().
        """
        for numero in range(1, capacidade_total + 1):
            cls.query(
                """
                INSERT INTO vaga_cama (numero_cama_pk, id_abrigo_fk, status)
                VALUES (%s, %s, 'livre')
                """,
                (numero, abrigo_id),
            )

    @classmethod
    def alocar_cama(cls, abrigo_id: int) -> int | None:
        """
        Encontra a primeira cama livre do abrigo e a marca como 'ocupada'.

        Returns:
            int | None: Número da cama alocada, ou None se não houver cama livre.
        """
        camas_livres = cls.query(
            """
            SELECT numero_cama_pk FROM vaga_cama
            WHERE id_abrigo_fk = %s AND status = 'livre'
            ORDER BY numero_cama_pk
            LIMIT 1
            """,
            (abrigo_id,),
        )
        if not camas_livres:
            return None

        numero_cama = camas_livres[0]["numero_cama_pk"]

        cls.query(
            """
            UPDATE vaga_cama SET status = 'ocupada'
            WHERE numero_cama_pk = %s AND id_abrigo_fk = %s
            """,
            (numero_cama, abrigo_id),
        )
        return numero_cama

    @classmethod
    def liberar_cama(cls, numero_cama: int, abrigo_id: int) -> None:
        """Marca a cama como 'livre' após a saída da pessoa."""
        cls.query(
            """
            UPDATE vaga_cama SET status = 'livre'
            WHERE numero_cama_pk = %s AND id_abrigo_fk = %s
            """,
            (numero_cama, abrigo_id),
        )

    @classmethod
    def listar_por_abrigo(cls, abrigo_id: int) -> list[dict]:
        """Lista todas as camas de um abrigo com seus status, ordenadas por número."""
        return (
            cls.query(
                """
            SELECT numero_cama_pk, id_abrigo_fk, status
            FROM vaga_cama
            WHERE id_abrigo_fk = %s
            ORDER BY numero_cama_pk
            """,
                (abrigo_id,),
            )
            or []
        )


class EstadiaModel(Database):
    """
    Gerencia a ocupação de camas específicas por pessoas (US08, US09).

    Entrada/saída NÃO requer prontuário, mas REQUER pessoa cadastrada.
    """

    @classmethod
    def _buscar_ativa_por_pessoa(cls, pessoa_id: int) -> dict | None:
        """Retorna a estadia ativa (sem data_saida) da pessoa, se houver."""
        rows = cls.query(
            """
            SELECT * FROM estadia
            WHERE id_pessoa_rua_fk = %s AND data_saida IS NULL
            ORDER BY data_entrada_pk DESC
            LIMIT 1
            """,
            (pessoa_id,),
        )
        return rows[0] if rows else None

    @classmethod
    def _buscar_ativa_por_cama(cls, numero_cama: int, abrigo_id: int) -> dict | None:
        """Retorna a estadia ativa de uma cama específica, se houver."""
        rows = cls.query(
            """
            SELECT * FROM estadia
            WHERE numero_cama_fk = %s AND id_abrigo_fk = %s AND data_saida IS NULL
            LIMIT 1
            """,
            (numero_cama, abrigo_id),
        )
        return rows[0] if rows else None

    @classmethod
    def registrar_entrada(cls, pessoa_id: int, abrigo_id: int) -> dict | None:
        """
        Registra a entrada de uma pessoa em um abrigo, alocando uma cama (US08).

        Ordem de operações:
          1. Verifica se a pessoa já tem estadia ativa.
          2. Aloca a primeira cama livre (VagaCamaModel.alocar_cama).
          3. Decrementa o contador de vagas do abrigo.
          4. Insere o registro em estadia.

        Raises:
            ValueError: Se a pessoa já tiver estadia ativa.
            RuntimeError: Se não houver cama livre no abrigo.
        """
        # 1. Pessoa já acolhida?
        if cls._buscar_ativa_por_pessoa(pessoa_id):
            raise ValueError(
                "A pessoa já está acolhida em um abrigo. "
                "Registre a saída antes de uma nova entrada."
            )

        # 2. Aloca cama livre
        numero_cama = VagaCamaModel.alocar_cama(abrigo_id)
        if numero_cama is None:
            raise RuntimeError("O abrigo não possui camas disponíveis no momento.")

        # 3. Atualiza contador do abrigo
        AbrigoModel.decrementar_vaga(abrigo_id)

        # 4. Registra a estadia
        cls.query(
            """
            INSERT INTO estadia (id_pessoa_rua_fk, numero_cama_fk, id_abrigo_fk)
            VALUES (%s, %s, %s)
            """,
            (pessoa_id, numero_cama, abrigo_id),
        )

        return cls._buscar_ativa_por_pessoa(pessoa_id)

    @classmethod
    def registrar_saida_por_cama(
        cls, numero_cama: int, abrigo_id: int, motivo_saida: str | None = None
    ) -> dict | None:
        """
        Registra a saída pelo número da cama e abrigo (US09).

        Args:
            numero_cama (int): Número da cama sendo desocupada.
            abrigo_id (int): ID do abrigo.
            motivo_saida (str, optional): Motivo da saída.

        Returns:
            dict | None: Estadia encerrada, ou None se a cama não tiver estadia ativa.
        """
        estadia = cls._buscar_ativa_por_cama(numero_cama, abrigo_id)
        if not estadia:
            return None  # controller → 404

        pessoa_id = estadia["id_pessoa_rua_fk"]

        cls.query(
            """
            UPDATE estadia
            SET data_saida = NOW(), motivo_saida = %s
            WHERE id_pessoa_rua_fk = %s AND data_saida IS NULL
            """,
            (motivo_saida, pessoa_id),
        )

        VagaCamaModel.liberar_cama(numero_cama, abrigo_id)
        AbrigoModel.incrementar_vaga(abrigo_id)

        rows = cls.query(
            """
            SELECT * FROM estadia
            WHERE id_pessoa_rua_fk = %s
            ORDER BY data_entrada_pk DESC
            LIMIT 1
            """,
            (pessoa_id,),
        )
        return rows[0] if rows else None

    @classmethod
    def registrar_saida(
        cls, pessoa_id: int, motivo_saida: str | None = None
    ) -> dict | None:
        """
        Registra a saída da pessoa, libera a cama e incrementa o contador (US09).

        Args:
            pessoa_id (int): ID da pessoa saindo.
            motivo_saida (str, optional): Motivo da saída.

        Returns:
            dict | None: Estadia encerrada, ou None se não houver estadia ativa.
        """
        estadia = cls._buscar_ativa_por_pessoa(pessoa_id)
        if not estadia:
            return None  # controller → 404

        # Encerra a estadia
        cls.query(
            """
            UPDATE estadia
            SET data_saida = NOW(), motivo_saida = %s
            WHERE id_pessoa_rua_fk = %s AND data_saida IS NULL
            """,
            (motivo_saida, pessoa_id),
        )

        # Libera a cama
        VagaCamaModel.liberar_cama(estadia["numero_cama_fk"], estadia["id_abrigo_fk"])

        # Incrementa o contador
        AbrigoModel.incrementar_vaga(estadia["id_abrigo_fk"])

        rows = cls.query(
            """
            SELECT * FROM estadia
            WHERE id_pessoa_rua_fk = %s
            ORDER BY data_entrada_pk DESC
            LIMIT 1
            """,
            (pessoa_id,),
        )
        return rows[0] if rows else None

    @classmethod
    def listar_por_pessoa(cls, pessoa_id: int) -> list[dict]:
        """Histórico completo de estadias de uma pessoa, mais recente primeiro."""
        return (
            cls.query(
                """
            SELECT e.*, vc.status AS status_cama
            FROM estadia e
            JOIN vaga_cama vc
              ON e.numero_cama_fk = vc.numero_cama_pk
             AND e.id_abrigo_fk   = vc.id_abrigo_fk
            WHERE e.id_pessoa_rua_fk = %s
            ORDER BY e.data_entrada_pk DESC
            """,
                (pessoa_id,),
            )
            or []
        )

    @classmethod
    def listar_por_abrigo(
        cls, abrigo_id: int, apenas_ativas: bool = False
    ) -> list[dict]:
        """
        Lista estadias de um abrigo.

        Args:
            abrigo_id (int): ID do abrigo.
            apenas_ativas (bool): Se True, retorna só quem está acolhido agora.
        """
        if apenas_ativas:
            query = """
                SELECT * FROM estadia
                WHERE id_abrigo_fk = %s AND data_saida IS NULL
                ORDER BY data_entrada_pk DESC
            """
        else:
            query = """
                SELECT * FROM estadia
                WHERE id_abrigo_fk = %s
                ORDER BY data_entrada_pk DESC
            """
        return cls.query(query, (abrigo_id,)) or []
