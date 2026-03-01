import uuid
from datetime import datetime, timezone

from app.extensions import db


class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    api_id = db.Column(
        db.String(50), unique=True, nullable=True, comment="nullable if user created"
    )
    source = db.Column(db.String(20), nullable=False, comment="tmdb, user, admin")
    title = db.Column(db.String(255), nullable=False)
    overview = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    popularity = db.Column(db.Float, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    created_by = db.Column(
        db.UUID,
        db.ForeignKey("users.id"),
        nullable=True,
        comment="nullable if from tmdb",
    )
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(
        db.String(20), nullable=False, default="active", comment="active, archived"
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    creator = db.relationship("User", back_populates="movies")
    genres = db.relationship(
        "Genre", secondary="movie_genres", back_populates="movies", lazy="select"
    )
    wishlists = db.relationship("Wishlist", back_populates="movie", lazy="select")
    images = db.relationship(
        "MovieImage",
        back_populates="movie",
        lazy="select",
        cascade="all, delete-orphan",
    )
    videos = db.relationship(
        "MovieVideo",
        back_populates="movie",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Movie {self.title}>"
