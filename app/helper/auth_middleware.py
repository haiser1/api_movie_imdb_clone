from functools import wraps

import jwt
from flask import request, g

from app.helper.base_response import response_error
from app.helper.jwt_handler import decode_token
from app.helper import logger as app_logger
from app.models.user import User


def jwt_required(f):
    """
    Decorator that enforces JWT authentication on a route.

    Extracts the Bearer token from the Authorization header,
    decodes it, validates the token type, and injects the
    current user into Flask's `g.current_user`.

    Returns 401 if the token is missing, invalid, or expired.
    Returns 401 if the associated user is not found.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            app_logger.json_logger.warning("Missing or invalid Authorization header")
            return response_error(
                message="Unauthorized",
                error="Missing or invalid Authorization header",
                status_code=401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            app_logger.json_logger.warning("Access token has expired")
            return response_error(
                message="Unauthorized",
                error="Token has expired",
                status_code=401,
            )
        except jwt.InvalidTokenError as e:
            app_logger.json_logger.warning(f"Invalid token: {str(e)}")
            return response_error(
                message="Unauthorized",
                error="Invalid token",
                status_code=401,
            )

        if payload.get("type") != "access":
            app_logger.json_logger.warning("Token is not an access token")
            return response_error(
                message="Unauthorized",
                error="Invalid token type",
                status_code=401,
            )

        user = User.query.get(payload["sub"])
        if not user:
            app_logger.json_logger.warning(
                f"User not found for token sub: {payload['sub']}"
            )
            return response_error(
                message="Unauthorized",
                error="User not found",
                status_code=401,
            )

        g.current_user = user
        return f(*args, **kwargs)

    return decorated
