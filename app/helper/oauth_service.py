from authlib.integrations.flask_client import OAuth

oauth = OAuth()


def init_oauth(app):
    """
    Initialize the OAuth client and register the Google provider.

    Uses OpenID Connect server metadata URL for auto-discovery
    of authorization, token, and userinfo endpoints.

    Args:
        app: Flask application instance.
    """
    from app.helper.logger import json_logger

    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=app.config["GOOGLE_DISCOVERY_URL"],
        client_kwargs={
            "scope": "openid email profile",
        },
    )
    json_logger.info("Google OAuth2 provider registered")


def get_google_client():
    """
    Get the registered Google OAuth client.

    Returns:
        The Authlib OAuth client for Google.
    """
    return oauth.google
