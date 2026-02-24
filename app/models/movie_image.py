import uuid
from datetime import datetime, timezone

from app.extensions import db


class MovieImage(db.Model):
    __tablename__ = "movie_images"

    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    movie_id = db.Column(db.UUID, db.ForeignKey("movies.id"), nullable=False)
    image_type = db.Column(db.String(20), nullable=False, comment="poster, backdrop")
    image_url = db.Column(db.Text, nullable=False)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    movie = db.relationship("Movie", back_populates="images")

    def __repr__(self):
        return f"<MovieImage {self.image_type} for movie={self.movie_id}>"
