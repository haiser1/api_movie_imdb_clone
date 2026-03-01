"""Admin service — business logic for admin operations."""

from flask import g
from app.schema.movie_schema import AdminMovieCreateSchema
from datetime import datetime, timezone

from sqlalchemy import func

from app.extensions import db
from app.models.movie import Movie
from app.models.user import User
from app.models.wishlist import Wishlist
from app.models.genre import Genre
from app.models.movie_genre import movie_genres
from app.helper.error_handler import NotFoundError
from app.helper.pagination import paginate
from app.services.movie_service import (
    _base_movie_query,
    _get_sort_column,
    get_movie_detail,
)


def get_dashboard():
    """Get aggregate analytics for admin dashboard.

    Uses efficient count queries instead of loading full objects.

    Returns:
        dict with total_movies, total_users, total_wishlists,
        movies_by_source, and popular_genres.
    """
    total_movies = (
        db.session.query(func.count(Movie.id))
        .filter(Movie.deleted_at.is_(None))
        .scalar()
    )

    total_users = db.session.query(func.count(User.id)).scalar()

    total_wishlists = db.session.query(func.count(Wishlist.id)).scalar()

    # Movies by source
    source_counts = (
        db.session.query(Movie.source, func.count(Movie.id))
        .filter(Movie.deleted_at.is_(None))
        .group_by(Movie.source)
        .all()
    )
    movies_by_source = {source: count for source, count in source_counts}

    # Popular genres (top 10)
    popular_genres = (
        db.session.query(Genre.name, func.count(movie_genres.c.movie_id))
        .join(movie_genres, Genre.id == movie_genres.c.genre_id)
        .join(Movie, Movie.id == movie_genres.c.movie_id)
        .filter(Movie.deleted_at.is_(None))
        .group_by(Genre.name)
        .order_by(func.count(movie_genres.c.movie_id).desc())
        .limit(10)
        .all()
    )

    return {
        "total_movies": total_movies,
        "total_users": total_users,
        "total_wishlists": total_wishlists,
        "movies_by_source": movies_by_source,
        "popular_genres": [
            {"genre": name, "count": count} for name, count in popular_genres
        ],
    }


def list_admin_movies(
    search=None,
    source=None,
    status=None,
    sort="created_at",
    order="desc",
    page=1,
    per_page=20,
):
    """List all movies for admin (including archived).

    Admin can see all statuses and sources.
    """
    query = _base_movie_query()

    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    if source:
        query = query.filter(Movie.source == source)
    if status:
        query = query.filter(Movie.status == status)

    sort_col = _get_sort_column(sort)
    if order == "asc":
        query = query.order_by(sort_col.asc().nullslast())
    else:
        query = query.order_by(sort_col.desc().nullslast())

    return paginate(query, page, per_page)


def create_admin_movie(data: AdminMovieCreateSchema):
    """Create a movie with admin-level fields.

    Admin can set popularity, rating, is_featured, and status.
    """
    movie = Movie(
        source="admin",
        created_by=g.current_user.get("sub"),
        title=data.title,
        overview=data.overview,
        release_date=data.release_date,
        popularity=data.popularity,
        rating=data.rating,
        is_featured=data.is_featured if data.is_featured is not None else False,
        status=data.status if data.status else "active",
    )

    if data.genre_ids:
        genres = Genre.query.filter(Genre.id.in_(data.genre_ids)).all()
        if not genres:
            raise NotFoundError(error="Genre not found, please provide valid genre ids")
        movie.genres = genres

    db.session.add(movie)
    db.session.commit()

    return get_movie_detail(movie.id)


def update_admin_movie(movie_id, data):
    """Update any movie (admin has full access).

    Raises:
        NotFoundError: If movie not found.
    """
    movie = Movie.query.filter(Movie.id == movie_id, Movie.deleted_at.is_(None)).first()
    if not movie:
        raise NotFoundError(error="Movie not found")

    if data.title is not None:
        movie.title = data.title
    if data.overview is not None:
        movie.overview = data.overview
    if data.release_date is not None:
        movie.release_date = data.release_date
    if data.popularity is not None:
        movie.popularity = data.popularity
    if data.rating is not None:
        movie.rating = data.rating
    if data.is_featured is not None:
        movie.is_featured = data.is_featured
    if data.status is not None:
        movie.status = data.status
    if data.genre_ids is not None:
        genres = Genre.query.filter(Genre.id.in_(data.genre_ids)).all()
        movie.genres = genres

    movie.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return get_movie_detail(movie.id)


def delete_admin_movie(movie_id):
    """Soft-delete any movie (admin can delete any source).

    Raises:
        NotFoundError: If movie not found.
    """
    movie = Movie.query.filter(Movie.id == movie_id, Movie.deleted_at.is_(None)).first()
    if not movie:
        raise NotFoundError(error="Movie not found")

    movie.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
