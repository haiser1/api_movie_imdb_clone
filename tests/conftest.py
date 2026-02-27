import pytest
from unittest.mock import patch
import uuid
import os

from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create Flask app with a test configuration using in-memory SQLite."""
    # Override DATABASE_URL before create_app() reads it
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-testing"

    # Patch OAuth to avoid real Google OAuth setup
    with patch("app.helper.oauth_service.init_oauth"):
        from app import create_app

        app = create_app()

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-for-unit-testing",
            "JWT_ACCESS_TOKEN_EXPIRES": 300,
            "JWT_REFRESH_TOKEN_EXPIRES": 604800,
        }
    )

    with app.app_context():
        _db.create_all()

    yield app

    with app.app_context():
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Clean database between tests to avoid unique constraint violations."""
    yield
    with app.app_context():
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Database session."""
    with app.app_context():
        yield _db.session


@pytest.fixture
def mock_user(app, db_session):
    """Create a test user in the database."""
    from app.models.user import User

    user = User(
        id=uuid.uuid4(),
        oauth_provider="google",
        oauth_id="test-oauth-id-123",
        name="Test User",
        email="test@example.com",
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def mock_admin(app, db_session):
    """Create a test admin user in the database."""
    from app.models.user import User

    admin = User(
        id=uuid.uuid4(),
        oauth_provider="google",
        oauth_id="admin-oauth-id-456",
        name="Admin User",
        email="admin@example.com",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def auth_headers(app, mock_user):
    """Generate valid JWT auth headers for mock_user."""
    with app.app_context():
        from app.helper.jwt_handler import create_access_token

        token = create_access_token(mock_user.id, mock_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(app, mock_admin):
    """Generate valid JWT auth headers for mock_admin."""
    with app.app_context():
        from app.helper.jwt_handler import create_access_token

        token = create_access_token(mock_admin.id, mock_admin.role)
    return {"Authorization": f"Bearer {token}"}
