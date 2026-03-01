"""Genre routes — public genre listing."""

from flask import Blueprint

from app.helper.base_response import response_success
from app.helper.error_handler import handle_errors
from app.services import genre_service

genre_bp = Blueprint("genres", __name__)


@genre_bp.route("/")
@handle_errors
def list_genres():
    """List all genres sorted alphabetically."""
    genres = genre_service.list_genres()
    return response_success("Genres retrieved", data=genres)
