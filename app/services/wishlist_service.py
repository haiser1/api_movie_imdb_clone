"""Wishlist service — business logic for wishlist operations."""

from app.extensions import db
from app.models.wishlist import Wishlist
from app.models.movie import Movie
from app.helper.error_handler import NotFoundError, ConflictError
from app.helper.pagination import paginate
from app.schema.movie_schema import serialize_movie

from sqlalchemy.orm import joinedload


def _serialize_wishlist(item):
    """Serialize a Wishlist model instance to dict."""
    return {
        "id": str(item.id),
        "movie_id": str(item.movie_id),
        "movie": serialize_movie(item.movie) if item.movie else None,
        "scheduled_watch_date": (
            item.scheduled_watch_date.isoformat() if item.scheduled_watch_date else None
        ),
        "reminder_sent": item.reminder_sent,
        "created_at": item.created_at.isoformat() if item.created_at else None,
    }


def list_wishlists(user_id, page=1, per_page=20):
    """List wishlist items for a user with movie details.

    Returns:
        tuple: (list of serialized wishlists, pagination meta)
    """
    query = (
        Wishlist.query.filter(Wishlist.user_id == user_id)
        .options(joinedload(Wishlist.movie))
        .order_by(Wishlist.created_at.desc())
    )
    items, meta = paginate(query, page, per_page)
    return [_serialize_wishlist(item) for item in items], meta


def create_wishlist(user_id, data):
    """Add a movie to user's wishlist.

    Raises:
        NotFoundError: If movie doesn't exist.
        ConflictError: If movie already in wishlist.
    """
    # Verify movie exists
    movie = Movie.query.filter(
        Movie.id == data.movie_id, Movie.deleted_at.is_(None)
    ).first()
    if not movie:
        raise NotFoundError(error="Movie not found")

    # Check duplicate
    existing = Wishlist.query.filter(
        Wishlist.user_id == user_id, Wishlist.movie_id == data.movie_id
    ).first()
    if existing:
        raise ConflictError(error="Movie already in wishlist")

    item = Wishlist(
        user_id=user_id,
        movie_id=data.movie_id,
        scheduled_watch_date=data.scheduled_watch_date,
    )
    db.session.add(item)
    db.session.commit()

    # Reload with movie relationship
    item = Wishlist.query.options(joinedload(Wishlist.movie)).get(item.id)
    return _serialize_wishlist(item)


def update_wishlist(user_id, wishlist_id, data):
    """Update a wishlist item (scheduled_watch_date).

    Raises:
        NotFoundError: If wishlist item not found or not owned by user.
    """
    item = Wishlist.query.filter(
        Wishlist.id == wishlist_id, Wishlist.user_id == user_id
    ).first()
    if not item:
        raise NotFoundError(error="Wishlist item not found")

    if data.scheduled_watch_date is not None:
        item.scheduled_watch_date = data.scheduled_watch_date

    db.session.commit()

    item = Wishlist.query.options(joinedload(Wishlist.movie)).get(item.id)
    return _serialize_wishlist(item)


def delete_wishlist(user_id, wishlist_id):
    """Remove a movie from user's wishlist.

    Raises:
        NotFoundError: If wishlist item not found or not owned by user.
    """
    item = Wishlist.query.filter(
        Wishlist.id == wishlist_id, Wishlist.user_id == user_id
    ).first()
    if not item:
        raise NotFoundError(error="Wishlist item not found")

    db.session.delete(item)
    db.session.commit()
