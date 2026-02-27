import jwt
from datetime import datetime, timezone, timedelta
from flask import current_app


def create_access_token(user_id: str, role: str) -> str:
    """
    Generate a JWT access token.

    Args:
        user_id: The user's UUID as string.
        role: The user's role (e.g., "user", "admin").

    Returns:
        Encoded JWT access token string.
    """
    expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def create_refresh_token(user_id: str) -> str:
    """
    Generate a JWT refresh token.

    Args:
        user_id: The user's UUID as string.

    Returns:
        Encoded JWT refresh token string.
    """
    expires = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT token string to decode.

    Returns:
        Decoded payload dictionary.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
    """
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"],
    )
