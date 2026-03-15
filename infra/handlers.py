from flask import jsonify
from infra.erros import InternalServerError


def register_error_handlers(app):
    @app.errorhandler(InternalServerError)
    def handle_app_error(error):
        return jsonify(error.to_dict()), error.status_code
