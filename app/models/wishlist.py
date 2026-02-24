import uuid
from datetime import datetime, timezone

from app.extensions import db


class Wishlist(db.Model):
    __tablename__ = "wishlists"

    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID, db.ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.UUID, db.ForeignKey("movies.id"), nullable=False)
    scheduled_watch_date = db.Column(db.Date, nullable=True)
    reminder_sent = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship("User", back_populates="wishlists")
    movie = db.relationship("Movie", back_populates="wishlists")

    def __repr__(self):
        return f"<Wishlist user={self.user_id} movie={self.movie_id}>"
