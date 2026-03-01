from functools import wraps

from pydantic import ValidationError

from app.helper.base_response import response_error
from app.helper.logger import json_logger


class AppError(Exception):
    """Base application error with HTTP status code."""

    def __init__(self, message: str, error: str = None, status_code: int = 500):
        self.message = message
        self.error = error or message
        self.status_code = status_code
        super().__init__(self.message)


class AuthError(AppError):
    """Authentication/authorization error (401)."""

    def __init__(self, message: str = "Unauthorized", error: str = None):
        super().__init__(message=message, error=error or message, status_code=401)


class NotFoundError(AppError):
    """Resource not found error (404)."""

    def __init__(self, message: str = "Not found", error: str = None):
        super().__init__(message=message, error=error or message, status_code=404)


class BadRequestError(AppError):
    """Bad request error (400)."""

    def __init__(self, message: str = "Bad request", error: str = None):
        super().__init__(message=message, error=error or message, status_code=400)


class ForbiddenError(AppError):
    """Forbidden error (403)."""

    def __init__(self, message: str = "Forbidden", error: str = None):
        super().__init__(message=message, error=error or message, status_code=403)


class ConflictError(AppError):
    """Conflict error (409)."""

    def __init__(self, message: str = "Conflict", error: str = None):
        super().__init__(message=message, error=error or message, status_code=409)


def handle_errors(f):
    """
    Decorator that catches exceptions and returns standardized error responses.

    Handles:
        - ValidationError (Pydantic) → 422
        - AppError (and subclasses: AuthError, NotFoundError, etc.) → dynamic status
        - Exception (unexpected) → 500
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            error_details = []
            for error in e.errors():
                error_details.append(
                    {
                        "field": ".".join(str(x) for x in error["loc"]),
                        "msg": error["msg"],
                        "type": error["type"],
                    }
                )
            return response_error(
                message="Validation Error", status_code=400, error=error_details
            )

        except AppError as e:
            json_logger.warning(f"{e.message}: {e.error}")
            return response_error(
                message=e.message,
                error=e.error,
                status_code=e.status_code,
            )
        except Exception as e:
            json_logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return response_error(
                message="Internal server error",
                status_code=500,
            )

    return decorated
