from flask import Blueprint, jsonify, request, url_for
from pydantic import ValidationError

from app.extensions import db
from app.models.user import User
from app.schema.auth import (
    TokenResponseSchema,
    RefreshTokenRequestSchema,
    UserResponseSchema,
)
from app.helper.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.helper.auth_middleware import jwt_required
from app.helper.oauth_service import get_google_client
from app.helper.logger import json_logger
from flask import g
import jwt as pyjwt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/google/login")
def google_login():
    """
    Initiate Google OAuth2 login flow.

    Redirects the user to Google's OAuth consent screen.
    After authorization, Google redirects back to the callback URL.

    Returns:
        Redirect to Google OAuth consent page.
    """
    google = get_google_client()
    redirect_uri = url_for("auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/callback")
def google_callback():
    """
    Handle the OAuth2 callback from Google.

    Exchanges the authorization code for tokens, fetches user info,
    creates or updates the user in the database, and returns JWT tokens.

    Returns:
        JSON response with access_token, refresh_token, token_type, and expires_in.
    """
    google = get_google_client()

    try:
        token = google.authorize_access_token()
    except Exception as e:
        json_logger.error(f"Failed to authorize with Google: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Authentication failed",
                "error": "Failed to authorize with Google",
            }
        ), 401

    user_info = token.get("userinfo")
    if not user_info:
        json_logger.error("Failed to retrieve user info from Google")
        return jsonify(
            {
                "success": False,
                "message": "Authentication failed",
                "error": "Failed to retrieve user information",
            }
        ), 401

    # Find or create the user
    user = User.query.filter_by(
        oauth_provider="google", oauth_id=str(user_info["sub"])
    ).first()

    if not user:
        # Check if user exists with same email
        user = User.query.filter_by(email=user_info["email"]).first()
        if user:
            # Link existing account with Google OAuth
            user.oauth_provider = "google"
            user.oauth_id = str(user_info["sub"])
            user.profile_picture = user_info.get("picture")
        else:
            # Create new user
            user = User(
                oauth_provider="google",
                oauth_id=str(user_info["sub"]),
                name=user_info.get("name", user_info["email"]),
                email=user_info["email"],
                profile_picture=user_info.get("picture"),
            )
            db.session.add(user)
    else:
        # Update existing user info
        user.name = user_info.get("name", user.name)
        user.profile_picture = user_info.get("picture", user.profile_picture)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        json_logger.error(f"Database error during user creation/update: {str(e)}")
        return jsonify(
            {
                "success": False,
                "message": "Authentication failed",
                "error": "Failed to save user data",
            }
        ), 500

    # Generate JWT tokens
    from flask import current_app

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)
    expires_in = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]

    response = TokenResponseSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )

    json_logger.info(f"User {user.email} authenticated via Google OAuth")

    return jsonify(
        {
            "success": True,
            "message": "Authentication successful",
            "data": response.model_dump(),
        }
    ), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Refresh an access token using a valid refresh token.

    Expects JSON body with `refresh_token` field.
    Returns a new access token if the refresh token is valid.

    Returns:
        JSON response with new access_token, refresh_token, token_type, and expires_in.
    """
    try:
        body = RefreshTokenRequestSchema(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify(
            {
                "success": False,
                "message": "Validation error",
                "error": str(e),
            }
        ), 422

    try:
        payload = decode_token(body.refresh_token)
    except pyjwt.ExpiredSignatureError:
        return jsonify(
            {
                "success": False,
                "message": "Unauthorized",
                "error": "Refresh token has expired",
            }
        ), 401
    except pyjwt.InvalidTokenError:
        return jsonify(
            {
                "success": False,
                "message": "Unauthorized",
                "error": "Invalid refresh token",
            }
        ), 401

    if payload.get("type") != "refresh":
        return jsonify(
            {
                "success": False,
                "message": "Unauthorized",
                "error": "Invalid token type",
            }
        ), 401

    user = User.query.get(payload["sub"])
    if not user:
        return jsonify(
            {
                "success": False,
                "message": "Unauthorized",
                "error": "User not found",
            }
        ), 401

    from flask import current_app

    access_token = create_access_token(user.id, user.role)
    new_refresh_token = create_refresh_token(user.id)
    expires_in = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]

    response = TokenResponseSchema(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
    )

    json_logger.info(f"Token refreshed for user {user.email}")

    return jsonify(
        {
            "success": True,
            "message": "Token refreshed successfully",
            "data": response.model_dump(),
        }
    ), 200


@auth_bp.route("/me")
@jwt_required
def get_current_user():
    """
    Get the current authenticated user's profile.

    Requires a valid JWT access token in the Authorization header.

    Returns:
        JSON response with user profile data.
    """
    user = g.current_user
    response = UserResponseSchema.model_validate(user)

    return jsonify(
        {
            "success": True,
            "message": "User profile retrieved",
            "data": response.model_dump(mode="json"),
        }
    ), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    """
    Logout placeholder endpoint.

    Since JWT is stateless, actual token invalidation would require
    a token blacklist (e.g., Redis). This endpoint serves as a
    placeholder for client-side token removal.

    Returns:
        JSON response confirming logout.
    """
    user = g.current_user
    json_logger.info(f"User {user.email} logged out")

    return jsonify(
        {
            "success": True,
            "message": "Logged out successfully",
        }
    ), 200
