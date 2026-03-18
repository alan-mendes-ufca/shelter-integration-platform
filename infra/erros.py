class InternalServerError(Exception):
    """Base class for application errors."""

    def __init__(self, name=None, message=None, action=None, status_code=None):
        self.name = name or "InternalServerError"
        self.message = message or "A unexpected error occurred."
        self.action = action or "Try again later."
        self.status_code = status_code or 500

    def to_dict(self):
        return {
            "message": self.message,
            "action": self.action,
            "name": self.name,
            "status_code": self.status_code,
        }


class ValidationError(InternalServerError):
    """Raised when a validation error occurs."""

    def __init__(self, message, action):
        self.name = "ValidationError"
        self.status_code = 400
        super().__init__(self.name, message, action, self.status_code)
