import uuid
from datetime import datetime, timezone

from app.extensions import db


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    movies = db.relationship("Movie", secondary="movie_genres", back_populates="genres", lazy="dynamic")

    def __repr__(self):
        return f"<Genre {self.name}>"
