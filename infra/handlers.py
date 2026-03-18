from flask import jsonify
from infra.erros import InternalServerError, ValidationError, NotFoundError


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):

        if isinstance(error, ValidationError) or isinstance(error, NotFoundError):
            return jsonify(error.to_dict()), error.status_code

        internal = InternalServerError()
        internal.__cause__ = error
        app.logger.exception("Unexpected error: %s", internal)
        return jsonify(internal.to_dict()), internal.status_code
