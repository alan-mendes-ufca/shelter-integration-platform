"""
Model: Abrigo + Vaga
====================

Estagiário, esses dois models trabalham juntos — são a dupla inseparável
do módulo de acolhimento.

`AbrigoModel` cuida do cadastro dos abrigos e da contagem de vagas.
`VagaModel` cuida das entradas e saídas individuais de pessoas nos abrigos.

O ponto mais delicado aqui é a consistência entre as duas tabelas:
quando uma pessoa ENTRA num abrigo, o `vagas_disponiveis` do abrigo deve
ser DECREMENTADO. Quando ela SAI, deve ser INCREMENTADO.

Isso idealmente seria feito em uma única TRANSAÇÃO para garantir que
as duas operações ocorram juntas ou nenhuma ocorra. Por enquanto, o
Database.query() executa uma query por vez, então a responsabilidade de
chamar as duas em sequência fica no controller. Anote isso como débito técnico.
"""

from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class AbrigoModel:
    """
    Gerencia o cadastro de abrigos e suas vagas disponíveis em tempo real.
    """

    @staticmethod
    def criar(dados: dict) -> dict | None:
        """
        Cadastra um novo abrigo no sistema.

        Args:
            dados (dict): Dados do abrigo.
                          Obrigatórios: 'nome', 'endereco', 'capacidade_total'
                          Opcionais: 'telefone'

        Returns:
            dict | None: Abrigo recém-criado.

        TODO (estagiário): No INSERT, `vagas_disponiveis` deve começar igual
                           a `capacidade_total` — abrigo novo = todas as vagas livres.
                           Não deixe o frontend definir `vagas_disponiveis` diretamente.
        """
        # TODO: Implementar
        raise NotImplementedError("AbrigoModel.criar() ainda não foi implementado.")

    @staticmethod
    def listar(apenas_com_vagas: bool = False) -> list[dict]:
        """
        Lista todos os abrigos ativos.

        Se `apenas_com_vagas=True`, filtra apenas abrigos com vagas disponíveis.
        Esse filtro é usado no momento do encaminhamento para acolhimento (US07).

        Args:
            apenas_com_vagas (bool): Se True, retorna apenas abrigos com vagas > 0.

        Returns:
            list[dict]: Lista de abrigos (com ou sem filtro de vagas).

        TODO (estagiário): Monte a query condicionalmente:
                           - Se apenas_com_vagas=True:  WHERE ativo=TRUE AND vagas_disponiveis > 0
                           - Se apenas_com_vagas=False: WHERE ativo=TRUE
                           Ordene por nome para facilitar a leitura pelo profissional.
        """
        # TODO: Implementar
        raise NotImplementedError("AbrigoModel.listar() ainda não foi implementado.")

    @staticmethod
    def decrementar_vaga(abrigo_id: int) -> bool:
        """
        Decrementa o contador de vagas disponíveis do abrigo em 1.

        Chamado pelo VagaModel.registrar_entrada() no controller.

        Args:
            abrigo_id (int): ID do abrigo.

        Returns:
            bool: True se decrementado com sucesso, False se sem vagas.

        TODO (estagiário): UPDATE abrigo SET vagas_disponiveis = vagas_disponiveis - 1
                           WHERE id = %s AND vagas_disponiveis > 0.
                           Se rowcount == 0, significa que não havia vagas disponíveis.
                           Retorne False nesse caso para o controller rejeitar a entrada
                           com HTTP 409 Conflict.
        """
        # TODO: Implementar
        raise NotImplementedError(
            "AbrigoModel.decrementar_vaga() ainda não foi implementado."
        )

    @staticmethod
    def incrementar_vaga(abrigo_id: int) -> bool:
        """
        Incrementa o contador de vagas disponíveis do abrigo em 1.

        Chamado pelo VagaModel.registrar_saida() no controller.

        Args:
            abrigo_id (int): ID do abrigo.

        Returns:
            bool: True se incrementado com sucesso.

        TODO (estagiário): UPDATE abrigo SET vagas_disponiveis = vagas_disponiveis + 1
                           WHERE id = %s AND vagas_disponiveis < capacidade_total.
                           O CHECK constraint no banco já protege contra ultrapassar
                           a capacidade, mas é boa prática verificar na aplicação também.
        """
        # TODO: Implementar
        raise NotImplementedError(
            "AbrigoModel.incrementar_vaga() ainda não foi implementado."
        )


class VagaModel:
    """
    Gerencia as ocupações individuais de vagas em abrigos.

    Importante: entrada/saída em abrigo não requer prontuário,
    mas REQUER que a pessoa já esteja cadastrada (US08, US09).
    """

    @staticmethod
    def registrar_entrada(pessoa_id: int, abrigo_id: int) -> dict | None:
        """
        Registra a entrada de uma pessoa em um abrigo (US08).

        Altera o status da vaga para 'ocupada' e dispara o
        decremento do contador no AbrigoModel.

        Args:
            pessoa_id (int): ID da pessoa entrando no abrigo.
            abrigo_id (int): ID do abrigo.

        Returns:
            dict | None: Registro da vaga criada.

        TODO (estagiário): Antes de inserir:
                           1. Chame AbrigoModel.decrementar_vaga(abrigo_id).
                              Se retornar False, aborte e retorne erro.
                           2. Verifique se a pessoa já tem uma vaga com status='ocupada'
                              em QUALQUER abrigo. Uma pessoa não pode estar em dois
                              abrigos ao mesmo tempo.
                           3. Se tudo OK, faça o INSERT em `vaga`.
        """
        # TODO: Implementar
        raise NotImplementedError(
            "VagaModel.registrar_entrada() ainda não foi implementado."
        )

    @staticmethod
    def registrar_saida(vaga_id: int) -> dict | None:
        """
        Registra a saída da pessoa do abrigo e libera a vaga (US09).

        Atualiza o status para 'liberada', preenche `saida_em`
        e incrementa o contador de vagas no AbrigoModel.

        Args:
            vaga_id (int): ID da vaga (registro de ocupação).

        Returns:
            dict | None: Vaga atualizada com status 'liberada'.

        TODO (estagiário): 1. Busque a vaga pelo ID. Se não existir ou já estiver
                              'liberada', retorne None (controller retorna 404/409).
                           2. Faça UPDATE vaga SET status='liberada', saida_em=NOW()
                              WHERE id=%s AND status='ocupada'.
                           3. Chame AbrigoModel.incrementar_vaga(abrigo_id) para
                              devolver a vaga ao contador do abrigo.
        """
        # TODO: Implementar
        raise NotImplementedError(
            "VagaModel.registrar_saida() ainda não foi implementado."
        )
