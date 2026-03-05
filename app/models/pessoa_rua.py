"""
Model: PessoaRua
================

Estagiário, o model é a camada que conversa diretamente com o banco de dados.
Ele não sabe nada de HTTP, não sabe nada de Flask — só sabe de SQL.

Toda a lógica de "como buscar", "como inserir", "como atualizar" fica aqui.
O controller vai chamar os métodos desse model e devolver o resultado como JSON.

Regra de ouro: NUNCA coloque lógica de banco de dados no controller.
              NUNCA coloque lógica de HTTP no model.
"""

from infra.database import Database  # noqa: F401 — usado nos TODOs abaixo


class PessoaRuaModel:
    """
    Representa e persiste os dados de pessoas em situação de rua.

    Essa é a tabela central do sistema — todo o resto (consentimento,
    atendimento, prontuário...) referencia o `pessoa_id` gerado aqui.

    O cadastro é SEMPRE possível, mesmo sem documentos.
    Campos obrigatórios mínimos: apelido + aparencia.
    """

    @staticmethod
    def criar(dados: dict) -> dict | None:
        """
        Insere uma nova pessoa no banco e retorna o registro criado.

        Estagiário: usamos `%s` como placeholder para evitar SQL Injection.
        NUNCA concatene strings diretamente numa query. Nunca.

        Args:
            dados (dict): Dicionário com os campos da pessoa.
                          Campos obrigatórios: 'apelido', 'aparencia'
                          Campos opcionais: 'nome_real', 'cpf', 'data_nascimento',
                                           'genero', 'endereco_ref', 'nivel_risco'

        Returns:
            dict | None: Registro da pessoa recém-criada ou None se falhar.

        TODO (estagiário): Implementar a query de INSERT e em seguida
                           um SELECT pelo lastrowid para retornar o registro completo.
                           Dica: cursor.lastrowid retorna o ID gerado pelo AUTO_INCREMENT.
        """
        # TODO: Implementar
        # Exemplo de estrutura esperada:
        #
        # query_insert = {
        #     'text': """
        #         INSERT INTO pessoa_rua (apelido, nome_real, cpf, data_nascimento,
        #                                genero, aparencia, endereco_ref, nivel_risco)
        #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        #     """,
        #     'values': (
        #         dados['apelido'],
        #         dados.get('nome_real'),
        #         dados.get('cpf'),
        #         dados.get('data_nascimento'),
        #         dados.get('genero'),
        #         dados['aparencia'],
        #         dados.get('endereco_ref'),
        #         dados.get('nivel_risco', 'baixo'),
        #     )
        # }
        # Database.query(query_insert)
        # ... buscar pelo ID gerado e retornar
        raise NotImplementedError("PessoaRuaModel.criar() ainda não foi implementado.")

    @staticmethod
    def buscar_por_id(pessoa_id: int) -> dict | None:
        """
        Busca uma pessoa pelo ID primário.

        Retorna None se não encontrar — o controller é responsável
        por transformar isso em um HTTP 404.

        Args:
            pessoa_id (int): ID da pessoa na tabela `pessoa_rua`.

        Returns:
            dict | None: Dados da pessoa ou None se não existir.

        TODO (estagiário): Implementar SELECT * FROM pessoa_rua WHERE id = %s.
                           fetchall() retorna uma lista; se vazia, retorne None.
                           Se tiver resultado, retorne result[0].
        """
        # TODO: Implementar
        raise NotImplementedError("PessoaRuaModel.buscar_por_id() ainda não foi implementado.")

    @staticmethod
    def buscar_por_apelido(apelido: str) -> list[dict]:
        """
        Busca pessoas cujo apelido contenha o termo informado (LIKE).

        Usado para evitar cadastros duplicados quando a pessoa já foi
        atendida anteriormente mas não tem documentos.

        Args:
            apelido (str): Termo de busca (parcial aceito).

        Returns:
            list[dict]: Lista de pessoas encontradas (pode ser vazia).

        TODO (estagiário): Use LIKE '%valor%' na query.
                           Atenção: o placeholder deve ser montado ANTES de passar
                           para o Database.query(), como: f'%{apelido}%'
                           Não coloque % dentro do %s — isso confunde o conector.
        """
        # TODO: Implementar
        raise NotImplementedError("PessoaRuaModel.buscar_por_apelido() ainda não foi implementado.")

    @staticmethod
    def atualizar(pessoa_id: int, dados: dict) -> dict | None:
        """
        Atualiza os dados gerais de uma pessoa.

        Estagiário: atualizações parciais (PATCH) são mais elegantes, mas
        para simplificar, aqui trabalhamos com PUT — o frontend manda tudo,
        nós atualizamos tudo. Campos não enviados mantêm valor anterior via
        lógica no controller (merge dos dados existentes + dados novos).

        Args:
            pessoa_id (int): ID da pessoa a ser atualizada.
            dados (dict): Campos a atualizar.

        Returns:
            dict | None: Registro atualizado ou None se não encontrado.

        TODO (estagiário): Implementar UPDATE + SELECT para retornar o estado atual.
        """
        # TODO: Implementar
        raise NotImplementedError("PessoaRuaModel.atualizar() ainda não foi implementado.")

    @staticmethod
    def atualizar_risco(pessoa_id: int, nivel_risco: str) -> dict | None:
        """
        Atualiza especificamente o nível de risco/vulnerabilidade da pessoa.

        Separado do `atualizar()` porque é uma ação com semântica própria —
        normalmente feita por profissional de saúde após avaliação (US06).

        Args:
            pessoa_id (int): ID da pessoa.
            nivel_risco (str): Um de: 'baixo', 'medio', 'alto', 'critico'.

        Returns:
            dict | None: Registro atualizado ou None se não encontrado.

        TODO (estagiário): Valide o valor de nivel_risco ANTES de mandar pro banco.
                           Os valores válidos estão no ENUM do SQL. Se vier algo
                           diferente, o MySQL vai rejeitar — melhor rejeitar antes
                           com uma mensagem clara pro usuário.
        """
        # TODO: Implementar
        raise NotImplementedError("PessoaRuaModel.atualizar_risco() ainda não foi implementado.")


