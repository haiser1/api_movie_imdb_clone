"""Unit tests for auth endpoints."""

import json
import uuid

import jwt as pyjwt


class TestRefreshToken:
    """Tests for POST /refresh endpoint."""

    def test_refresh_token_missing_body(self, client):
        """Should return 422 when request body is missing."""
        response = client.post(
            "/api/auth/refresh",
            content_type="application/json",
            data=json.dumps({}),
        )
        assert response.status_code == 422
        data = response.get_json()
        assert data["success"] is False
        assert data["message"] == "Validation error"

    def test_refresh_token_invalid_token(self, client):
        """Should return 401 when refresh token is invalid."""
        response = client.post(
            "/api/auth/refresh",
            content_type="application/json",
            data=json.dumps({"refresh_token": "invalid-token"}),
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
        assert data["error"] == "Invalid refresh token"

    def test_refresh_token_expired(self, client, app):
        """Should return 401 when refresh token is expired."""
        from datetime import datetime, timezone, timedelta

        payload = {
            "sub": str(uuid.uuid4()),
            "type": "refresh",
            "iat": datetime.now(timezone.utc) - timedelta(days=30),
            "exp": datetime.now(timezone.utc) - timedelta(days=1),
        }
        expired_token = pyjwt.encode(
            payload, app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )

        response = client.post(
            "/api/auth/refresh",
            content_type="application/json",
            data=json.dumps({"refresh_token": expired_token}),
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "Refresh token has expired"

    def test_refresh_token_wrong_type(self, client, app):
        """Should return 401 when token type is not 'refresh'."""
        from datetime import datetime, timezone, timedelta

        payload = {
            "sub": str(uuid.uuid4()),
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        access_token = pyjwt.encode(
            payload, app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )

        response = client.post(
            "/api/auth/refresh",
            content_type="application/json",
            data=json.dumps({"refresh_token": access_token}),
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "Invalid token type"

    def test_refresh_token_user_not_found(self, client, app):
        """Should return 401 when user from token does not exist."""
        from datetime import datetime, timezone, timedelta

        payload = {
            "sub": str(uuid.uuid4()),
            "type": "refresh",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = pyjwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")

        response = client.post(
            "/api/auth/refresh",
            content_type="application/json",
            data=json.dumps({"refresh_token": token}),
        )
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "User not found"

    def test_refresh_token_success(self, client, app, mock_user):
        """Should return 200 with new tokens when refresh token is valid."""
        with app.app_context():
            from app.helper.jwt_handler import create_refresh_token

            refresh_token = create_refresh_token(mock_user.id)

        response = client.post(
            "/api/auth/refresh",
            content_type="application/json",
            data=json.dumps({"refresh_token": refresh_token}),
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["message"] == "Token refreshed successfully"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "Bearer"
        assert data["data"]["expires_in"] == 300


class TestGetCurrentUser:
    """Tests for GET /me endpoint."""

    def test_me_no_auth(self, client):
        """Should return 401 when no Authorization header."""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
        assert data["error"] == "Missing or invalid Authorization header"

    def test_me_invalid_token(self, client):
        """Should return 401 when token is invalid."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_me_success(self, client, auth_headers, mock_user):
        """Should return 200 with user profile when authenticated."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["message"] == "User profile retrieved"
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["name"] == "Test User"
        assert data["data"]["role"] == "user"


class TestLogout:
    """Tests for POST /logout endpoint."""

    def test_logout_no_auth(self, client):
        """Should return 401 when not authenticated."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 401

    def test_logout_success(self, client, auth_headers):
        """Should return 200 when authenticated."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["message"] == "Logged out successfully"


class TestBaseResponse:
    """Tests for base response helper functions."""

    def test_response_success_with_data(self, app):
        """Should return success response with data."""
        with app.app_context():
            from app.helper.base_response import response_success

            response, status_code = response_success(
                message="OK", data={"key": "value"}
            )
            data = response.get_json()
            assert status_code == 200
            assert data["success"] is True
            assert data["message"] == "OK"
            assert data["data"] == {"key": "value"}

    def test_response_success_without_data(self, app):
        """Should return success response without data key."""
        with app.app_context():
            from app.helper.base_response import response_success

            response, status_code = response_success(message="Done")
            data = response.get_json()
            assert status_code == 200
            assert data["success"] is True
            assert "data" not in data

    def test_response_error(self, app):
        """Should return error response."""
        with app.app_context():
            from app.helper.base_response import response_error

            response, status_code = response_error(
                message="Bad request", error="Invalid input", status_code=400
            )
            data = response.get_json()
            assert status_code == 400
            assert data["success"] is False
            assert data["message"] == "Bad request"
            assert data["error"] == "Invalid input"


class TestErrorHandlerDecorator:
    """Tests for @handle_errors decorator."""

    def test_handles_app_error(self, app):
        """Should catch AppError and return proper response."""
        from app.helper.error_handler import handle_errors, AuthError

        @handle_errors
        def raise_auth_error():
            raise AuthError(error="Token expired")

        with app.app_context():
            response, status_code = raise_auth_error()
            data = response.get_json()
            assert status_code == 401
            assert data["success"] is False
            assert data["error"] == "Token expired"

    def test_handles_generic_exception(self, app):
        """Should catch generic Exception and return 500."""
        from app.helper.error_handler import handle_errors

        @handle_errors
        def raise_generic():
            raise RuntimeError("Something broke")

        with app.app_context():
            response, status_code = raise_generic()
            data = response.get_json()
            assert status_code == 500
            assert data["success"] is False
            assert data["message"] == "Internal server error"
