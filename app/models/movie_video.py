import uuid
from datetime import datetime, timezone

from app.extensions import db


class MovieVideo(db.Model):
    __tablename__ = "movie_videos"

    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    movie_id = db.Column(db.UUID, db.ForeignKey("movies.id"), nullable=False)
    video_type = db.Column(db.String(20), nullable=False, comment="trailer, teaser")
    site = db.Column(db.String(50), nullable=False, comment="youtube, vimeo")
    video_key = db.Column(db.String(255), nullable=False, comment="youtube key")
    official = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    movie = db.relationship("Movie", back_populates="videos")

    def __repr__(self):
        return f"<MovieVideo {self.video_type} for movie={self.movie_id}>"
