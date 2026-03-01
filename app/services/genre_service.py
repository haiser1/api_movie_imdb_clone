"""Genre service — business logic for genre operations."""

from app.models.genre import Genre


def list_genres():
    """List all genres ordered by name.

    Returns:
        list of dicts with genre id and name.
    """
    genres = Genre.query.order_by(Genre.name.asc()).all()
    return [{"id": str(g.id), "name": g.name} for g in genres]
