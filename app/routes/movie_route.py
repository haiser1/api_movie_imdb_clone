"""Movie routes — public browsing and user movie management."""

from flask import Blueprint, request, g

from app.helper.auth_middleware import jwt_required
from app.helper.base_response import response_success
from app.helper.error_handler import handle_errors
from app.helper.pagination import get_pagination_params
from app.schema.movie_schema import (
    MovieCreateSchema,
    MovieUpdateSchema,
    serialize_movie,
)
from app.services import movie_service

movie_bp = Blueprint("movies", __name__)


# ==================== PUBLIC ====================


@movie_bp.route("/")
@handle_errors
def list_movies():
    """List all movies with search, filter, sort, pagination."""
    page, per_page = get_pagination_params()
    movies, meta = movie_service.list_movies(
        search=request.args.get("search"),
        genre_id=request.args.get("genre_id"),
        source=request.args.get("source"),
        status=request.args.get("status", "active"),
        release_date_from=request.args.get("release_date_from"),
        release_date_to=request.args.get("release_date_to"),
        sort=request.args.get("sort", "created_at"),
        order=request.args.get("order", "desc"),
        page=page,
        per_page=per_page,
    )
    return response_success(
        "Movies retrieved",
        data=[serialize_movie(m) for m in movies],
        meta=meta,
    )


@movie_bp.route("/popular")
@handle_errors
def get_popular_movies():
    """Get movies sorted by popularity."""
    page, per_page = get_pagination_params()
    movies, meta = movie_service.get_popular_movies(page, per_page)
    return response_success(
        "Popular movies retrieved",
        data=[serialize_movie(m) for m in movies],
        meta=meta,
    )


@movie_bp.route("/<id>")
@handle_errors
def get_movie_detail(id):
    """Get detailed movie information."""
    movie = movie_service.get_movie_detail(id)
    return response_success("Movie detail retrieved", data=serialize_movie(movie))


# ==================== USER MOVIES ====================


@movie_bp.route("/me")
@jwt_required
@handle_errors
def list_my_movies():
    """List movies created by the current user."""
    page, per_page = get_pagination_params()
    movies, meta = movie_service.list_user_movies(
        g.current_user.get("sub"), page, per_page
    )
    return response_success(
        "Your movies retrieved",
        data=[serialize_movie(m) for m in movies],
        meta=meta,
    )


@movie_bp.route("/user", methods=["POST"])
@jwt_required
@handle_errors
def create_user_movie():
    """Create a new user movie."""
    body = MovieCreateSchema(**request.get_json())
    movie = movie_service.create_user_movie(g.current_user.get("sub"), body)
    return response_success(
        "Movie created", data=serialize_movie(movie), status_code=201
    )


@movie_bp.route("/user/<id>", methods=["PUT"])
@jwt_required
@handle_errors
def update_user_movie(id):
    """Update a movie owned by the current user."""
    body = MovieUpdateSchema(**request.get_json())
    movie = movie_service.update_user_movie(g.current_user.get("sub"), id, body)
    return response_success("Movie updated", data=serialize_movie(movie))


@movie_bp.route("/user/<id>", methods=["DELETE"])
@jwt_required
@handle_errors
def delete_user_movie(id):
    """Soft-delete a movie owned by the current user."""
    movie_service.delete_user_movie(g.current_user.get("sub"), id)
    return response_success("Movie deleted")
