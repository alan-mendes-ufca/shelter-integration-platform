from flask import jsonify
from infra.erros import InternalServerError, ValidationError, NotFoundError
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):

        if isinstance(error, ValidationError) or isinstance(error, NotFoundError):
            return jsonify(error.to_dict()), error.status_code

        if isinstance(error, HTTPException):
            return (
                jsonify(
                    {
                        "name": error.name,
                        "message": error.description,
                        "action": "Verifique a URL e tente novamente.",
                        "status_code": error.code,
                    }
                ),
                error.code,
            )

        internal = InternalServerError()
        internal.__cause__ = error
        app.logger.exception("Unexpected error: %s", internal)
        return jsonify(internal.to_dict()), internal.status_code
