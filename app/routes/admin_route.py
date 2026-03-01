"""Admin routes — dashboard, movie management, and TMDB sync."""

from flask import Blueprint, request

from app.models.sync_log import SyncLog

from app.helper.auth_middleware import admin_required
from app.helper.tmdb_helper import serialize_sync_log
from app.helper.base_response import response_success
from app.helper.error_handler import handle_errors
from app.helper.pagination import get_pagination_params
from app.schema.movie_schema import (
    AdminMovieCreateSchema,
    AdminMovieUpdateSchema,
    serialize_movie,
)
from app.services import admin_service, tmdb_service

admin_bp = Blueprint("admin", __name__)


# ==================== DASHBOARD ====================


@admin_bp.route("/dashboard")
@admin_required
@handle_errors
def get_dashboard():
    """Get analytics dashboard data."""
    data = admin_service.get_dashboard()
    return response_success("Dashboard retrieved", data=data)


# ==================== ADMIN MOVIES ====================


@admin_bp.route("/movies")
@admin_required
@handle_errors
def list_admin_movies():
    """List all movies (admin view, includes archived)."""
    page, per_page = get_pagination_params()
    movies, meta = admin_service.list_admin_movies(
        search=request.args.get("search"),
        source=request.args.get("source"),
        status=request.args.get("status"),
        sort=request.args.get("sort_by", "created_at"),
        order=request.args.get("order_by", "desc"),
        page=page,
        per_page=per_page,
    )
    return response_success(
        "Movies retrieved",
        data=[serialize_movie(m) for m in movies],
        meta=meta,
    )


@admin_bp.route("/movies", methods=["POST"])
@admin_required
@handle_errors
def create_admin_movie():
    """Create a movie with admin-level fields."""
    body = AdminMovieCreateSchema(**request.get_json())
    movie = admin_service.create_admin_movie(body)
    return response_success(
        "Movie created", data=serialize_movie(movie), status_code=201
    )


@admin_bp.route("/movies/<id>", methods=["PUT"])
@admin_required
@handle_errors
def update_admin_movie(id):
    """Update any movie (admin has full access)."""
    body = AdminMovieUpdateSchema(**request.get_json())
    movie = admin_service.update_admin_movie(id, body)
    return response_success("Movie updated", data=serialize_movie(movie))


@admin_bp.route("/movies/<id>", methods=["DELETE"])
@admin_required
@handle_errors
def delete_admin_movie(id):
    """Soft-delete any movie."""
    admin_service.delete_admin_movie(id)
    return response_success("Movie deleted")


# ==================== TMDB SYNC ====================


@admin_bp.route("/sync/movies", methods=["POST"])
@admin_required
@handle_errors
def trigger_movie_sync():
    """Sync movies from TMDB (background).

    Query params:
        mode: "full" (default) or "changes" (incremental, last 14 days)
        resume: "true" to resume from last failed position (full mode only)
    """
    mode = request.args.get("mode", "full").lower()
    resume = request.args.get("resume", "false").lower() == "true"

    sync_type = "changes" if mode == "changes" else "movies"

    try:
        data = tmdb_service.start_sync_background(sync_type, resume=resume)
    except ValueError as e:
        return response_success(str(e), status_code=409)

    msg = (
        "Incremental sync started (last 14 days changes)"
        if sync_type == "changes"
        else "Full movie sync started in background"
    )
    return response_success(msg, data=data, status_code=202)


@admin_bp.route("/sync/status")
@admin_required
@handle_errors
def get_sync_status():
    """Get current sync status (live progress or last completed sync)."""
    data = tmdb_service.get_sync_status()
    return response_success("Sync status retrieved", data=data)


@admin_bp.route("/sync/last-sync")
@admin_required
@handle_errors
def get_last_sync():
    """Get the last completed sync log from the database."""
    log = SyncLog.query.order_by(SyncLog.created_at.desc()).first()
    if not log:
        return response_success("No sync has been run yet", data=None)
    return response_success("Last sync retrieved", data=serialize_sync_log(log))
