"""
Fábrica da aplicação Flask — Application Factory Pattern
=========================================================

Estagiário, esse arquivo é o coração da aplicação Flask.

Usamos o padrão "Application Factory" (create_app) para:
1. Facilitar a criação de múltiplas instâncias do app (ex: teste vs produção).
2. Evitar importações circulares — o app só é criado quando chamado.
3. Manter o código organizado e testável.

Cada módulo do sistema tem seu próprio Blueprint registrado aqui.
Quando você criar um novo controller, lembre-se de:
  1. Importar o blueprint no topo desse arquivo.
  2. Registrá-lo com app.register_blueprint().
"""

from flask import Flask, redirect

from infra.handlers import register_error_handlers

# Controllers legados (exemplo)
from .controllers.blueprint_example import blueprint_example

# Controllers do sistema de atendimento
from .controllers.pessoa_rua import pessoas_bp
from .controllers.consentimentos import consentimentos_bp
from .controllers.atendimentos import atendimentos_bp
from .controllers.prontuarios import profissionais_bp, prontuarios_bp
from .controllers.abrigos import abrigos_bp, vagas_bp
from .controllers.encaminhamentos import encaminhamentos_bp
from .docs.swagger import init_swagger

API_PREFIX = "/api/v1"  # Prefixo comum para todas as rotas da API


def create_app():
    """
    Cria e configura a instância da aplicação Flask.

    Todos os blueprints (controllers) são registrados aqui.
    A ordem de registro não importa para o funcionamento,
    mas mantenha organizado por módulo para facilitar a leitura.

    Returns:
        Flask: Instância configurada da aplicação.
    """
    app = Flask(__name__)

    register_error_handlers(app)

    # Blueprint de exemplo (pode remover quando o sistema estiver completo)
    app.register_blueprint(blueprint_example)

    # ── Sistema de Atendimento ─────────────────────────────────────────────────
    app.register_blueprint(
        pessoas_bp, url_prefix=f"{API_PREFIX}/pessoas"
    )  # GET/POST /pessoas
    app.register_blueprint(
        consentimentos_bp, url_prefix=f"{API_PREFIX}/consentimentos"
    )  # GET/POST /consentimentos
    app.register_blueprint(
        atendimentos_bp, url_prefix=f"{API_PREFIX}/atendimentos"
    )  # GET/POST /atendimentos
    app.register_blueprint(
        profissionais_bp, url_prefix=f"{API_PREFIX}/profissionais"
    )  # GET/POST /profissionais
    app.register_blueprint(
        prontuarios_bp, url_prefix=f"{API_PREFIX}/prontuarios"
    )  # GET/POST /prontuarios
    app.register_blueprint(
        abrigos_bp, url_prefix=f"{API_PREFIX}/abrigos"
    )  # GET/POST /abrigos
    app.register_blueprint(
        vagas_bp, url_prefix=f"{API_PREFIX}/vagas"
    )  # POST /vagas/entrada, PUT /vagas/:id/saida
    app.register_blueprint(
        encaminhamentos_bp, url_prefix=f"{API_PREFIX}/encaminhamentos"
    )  # GET/POST /encaminhamentos

    init_swagger(app)

    @app.route("/", methods=["GET"])
    def index():
        return redirect("/docs/")

    return app
