"""Movie service — business logic for movie operations."""

from flask import g
from datetime import datetime, timezone

from sqlalchemy.orm import joinedload, subqueryload

from app.extensions import db
from app.models.movie import Movie
from app.models.genre import Genre
from app.helper.error_handler import NotFoundError, ForbiddenError
from app.helper.pagination import paginate


def _base_movie_query(include_deleted=False):
    """Base query with eager loading and soft-delete filter."""
    query = Movie.query.options(
        joinedload(Movie.genres),
        subqueryload(Movie.images),
        subqueryload(Movie.videos),
    )
    if not include_deleted:
        query = query.filter(Movie.deleted_at.is_(None))
    return query


def _get_sort_column(sort_field):
    """Map sort field name to SQLAlchemy column."""
    sort_map = {
        "title": Movie.title,
        "release_date": Movie.release_date,
        "popularity": Movie.popularity,
        "rating": Movie.rating,
        "created_at": Movie.created_at,
    }
    return sort_map.get(sort_field, Movie.created_at)


def list_movies(
    search=None,
    genre_id=None,
    source=None,
    status="active",
    release_date_from=None,
    release_date_to=None,
    sort="created_at",
    order="desc",
    page=1,
    per_page=20,
):
    """List movies with search, filter, sort, and pagination.

    Returns:
        tuple: (list of Movie, pagination meta dict)
    """
    query = _base_movie_query()

    # Filters
    if status:
        query = query.filter(Movie.status == status)
    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    if source:
        query = query.filter(Movie.source == source)
    if genre_id:
        query = query.filter(Movie.genres.any(Genre.id == genre_id))
    if release_date_from:
        query = query.filter(Movie.release_date >= release_date_from)
    if release_date_to:
        query = query.filter(Movie.release_date <= release_date_to)

    # Sort
    sort_col = _get_sort_column(sort)
    if order == "asc":
        query = query.order_by(sort_col.asc().nullslast())
    else:
        query = query.order_by(sort_col.desc().nullslast())

    return paginate(query, page, per_page)


def get_popular_movies(page=1, per_page=20):
    """Get movies sorted by popularity descending."""
    query = (
        _base_movie_query()
        .filter(Movie.status == "active")
        .order_by(Movie.popularity.desc().nullslast())
    )
    return paginate(query, page, per_page)


def get_movie_detail(movie_id):
    """Get single movie with all relationships.

    Videos are fetched on-demand from TMDB API for tmdb-sourced movies
    and cached in the database for subsequent requests.

    Raises:
        NotFoundError: If movie not found or deleted.
    """
    from app.services import tmdb_service

    movie = _base_movie_query().filter(Movie.id == movie_id).first()
    if not movie:
        raise NotFoundError(error="Movie not found")

    # On-demand: fetch & cache videos from TMDB if not yet in DB
    tmdb_service.fetch_and_cache_videos(movie)

    return movie


def list_user_movies(user_id, page=1, per_page=20):
    """List movies created by a specific user."""
    role = g.current_user.get("role") or "user"
    query = (
        _base_movie_query()
        .filter(
            Movie.created_by == user_id,
            Movie.source == role,
        )
        .order_by(Movie.created_at.desc())
    )
    return paginate(query, page, per_page)


def create_user_movie(user_id, data):
    """Create a new user movie.

    Args:
        user_id: UUID of the creating user.
        data: MovieCreateSchema validated data.

    Returns:
        Movie instance with loaded relationships.
    """
    movie = Movie(
        source="user",
        title=data.title,
        overview=data.overview,
        release_date=data.release_date,
        created_by=user_id,
    )

    if data.genre_ids:
        genres = Genre.query.filter(Genre.id.in_(data.genre_ids)).all()
        movie.genres = genres

    db.session.add(movie)
    db.session.commit()

    # Reload with relationships
    return get_movie_detail(movie.id)


def update_user_movie(user_id, movie_id, data):
    """Update a movie owned by the current user.

    Raises:
        NotFoundError: If movie not found.
        ForbiddenError: If user is not the owner.
    """
    movie = Movie.query.filter(Movie.id == movie_id, Movie.deleted_at.is_(None)).first()
    if not movie:
        raise NotFoundError(error="Movie not found")
    if str(movie.created_by) != str(user_id):
        raise ForbiddenError(error="You can only update your own movies")

    if data.title is not None:
        movie.title = data.title
    if data.overview is not None:
        movie.overview = data.overview
    if data.release_date is not None:
        movie.release_date = data.release_date
    if data.genre_ids is not None:
        genres = Genre.query.filter(Genre.id.in_(data.genre_ids)).all()
        movie.genres = genres

    movie.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return get_movie_detail(movie.id)


def delete_user_movie(user_id, movie_id):
    """Soft-delete a movie owned by the current user.

    Raises:
        NotFoundError: If movie not found.
        ForbiddenError: If user is not the owner.
    """
    movie = Movie.query.filter(Movie.id == movie_id, Movie.deleted_at.is_(None)).first()
    if not movie:
        raise NotFoundError(error="Movie not found")
    if str(movie.created_by) != str(user_id):
        raise ForbiddenError(error="You can only delete your own movies")

    movie.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
