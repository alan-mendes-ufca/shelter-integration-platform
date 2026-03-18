"""
Model: Abrigo + Vaga
====================

`AbrigoModel` cuida do cadastro dos abrigos e da contagem de vagas.
`VagaModel` cuida das entradas e saídas individuais de pessoas nos abrigos.

DÉBITO TÉCNICO: entrada/saída envolve duas queries (vaga + contador do abrigo).
Idealmente seriam uma transação atômica. Por enquanto são executadas em sequência
— se a segunda falhar, o sistema ficará inconsistente. Implementar suporte a
transações no Database.query() quando possível.

Decisões de design (divergências do DER original documentadas):
- DER tem vaga_cama + estadia separadas; código usa tabela única `vaga`.
  Motivo: simplificação acordada — não controlamos cama específica, só ocupação.
- DER liga abrigo a gestor/historico_gestao; essa parte não está implementada.
  Motivo: fora do escopo atual, registrado como débito técnico.
- DER liga atendimento a abrigo via FK; código usa campo `unidade` (texto livre).
  Motivo: atendimento pode ocorrer fora de abrigos cadastrados.
"""

from infra.database import Database


class AbrigoModel(Database):
    """
    Gerencia o cadastro de abrigos e suas vagas disponíveis em tempo real.
    """

    @classmethod
    def criar(cls, dados: dict) -> dict | None:
        """
        Cadastra um novo abrigo no sistema.

        Args:
            dados (dict): Dados do abrigo.
                          Obrigatórios: 'nome', 'endereco', 'capacidade_total'
                          Opcionais: 'telefone'

        Returns:
            dict | None: Abrigo recém-criado.

        Nota: vagas_disponiveis começa igual a capacidade_total.
              O frontend não pode definir vagas_disponiveis diretamente.
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

        if telefone:
            telefone = str(telefone).strip() or None

        query_insert = """
            INSERT INTO abrigo (nome, endereco, capacidade_total, vagas_disponiveis, telefone)
            VALUES (%s, %s, %s, %s, %s)
        """
        # vagas_disponiveis começa igual a capacidade_total
        params_insert = (nome, endereco, capacidade_total, capacidade_total, telefone)

        abrigo_id = cls.query(query_insert, params_insert)

        rows = cls.query("SELECT * FROM abrigo WHERE id_abrigo = %s", (abrigo_id,))
        return rows[0] if rows else None

    @classmethod
    def listar(cls, apenas_com_vagas: bool = False) -> list[dict]:
        """
        Lista todos os abrigos ativos.

        Args:
            apenas_com_vagas (bool): Se True, retorna apenas abrigos com vagas > 0.

        Returns:
            list[dict]: Lista de abrigos ordenada por nome.
        """
        if apenas_com_vagas:
            query = """
                SELECT * FROM abrigo
                WHERE ativo = TRUE AND vagas_disponiveis > 0
                ORDER BY nome
            """
        else:
            query = """
                SELECT * FROM abrigo
                WHERE ativo = TRUE
                ORDER BY nome
            """

        rows = cls.query(query)
        return rows or []

    @classmethod
    def decrementar_vaga(cls, abrigo_id: int) -> bool:
        """
        Decrementa vagas_disponiveis do abrigo em 1, somente se houver vagas.

        Returns:
            bool: True se decrementado, False se não havia vagas disponíveis.
        """
        query = """
            UPDATE abrigo
            SET vagas_disponiveis = vagas_disponiveis - 1
            WHERE id_abrigo = %s AND vagas_disponiveis > 0
        """
        # query() retorna [] para UPDATE — precisamos saber se afetou alguma linha.
        # Usamos uma verificação antes + depois para contornar a limitação do Database.query().
        abrigo_antes = cls.query(
            "SELECT vagas_disponiveis FROM abrigo WHERE id_abrigo = %s", (abrigo_id,)
        )
        if not abrigo_antes or abrigo_antes[0]["vagas_disponiveis"] <= 0:
            return False

        cls.query(query, (abrigo_id,))
        return True

    @classmethod
    def incrementar_vaga(cls, abrigo_id: int) -> bool:
        """
        Incrementa vagas_disponiveis do abrigo em 1, respeitando a capacidade total.

        Returns:
            bool: True se incrementado com sucesso.
        """
        query = """
            UPDATE abrigo
            SET vagas_disponiveis = vagas_disponiveis + 1
            WHERE id_abrigo = %s AND vagas_disponiveis < capacidade_total
        """
        cls.query(query, (abrigo_id,))
        return True


class VagaModel(Database):
    """
    Gerencia as ocupações individuais de vagas em abrigos.

    Importante: entrada/saída NÃO requer prontuário,
    mas REQUER que a pessoa já esteja cadastrada (US08, US09).
    """

    @classmethod
    def _buscar_por_id(cls, vaga_id: int) -> dict | None:
        """Busca um registro de vaga pelo ID."""
        rows = cls.query("SELECT * FROM vaga WHERE id_vaga = %s", (vaga_id,))
        return rows[0] if rows else None

    @classmethod
    def registrar_entrada(cls, pessoa_id: int, abrigo_id: int) -> dict | None:
        """
        Registra a entrada de uma pessoa em um abrigo (US08).

        Ordem de operações:
          1. Verifica se a pessoa já está acolhida em algum abrigo.
          2. Tenta decrementar a vaga do abrigo (falha se lotado).
          3. Insere o registro na tabela `vaga`.

        Returns:
            dict | None: Registro da vaga criada.

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
            dict | None: Vaga atualizada com status 'liberada',
                         ou None se a vaga não existir ou já estiver liberada.
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
            UPDATE vaga
            SET status = 'liberada', saida_em = NOW()
            WHERE id_vaga = %s AND status = 'ocupada'
            """,
            (vaga_id,),
        )

        # 3. Devolve a vaga ao contador do abrigo
        AbrigoModel.incrementar_vaga(vaga["abrigo_id"])

        return cls._buscar_por_id(vaga_id)
