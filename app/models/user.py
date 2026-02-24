import uuid
from datetime import datetime, timezone

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    oauth_provider = db.Column(db.String(50), nullable=True, comment="google, github")
    oauth_id = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user", comment="user, admin")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    movies = db.relationship("Movie", back_populates="creator", lazy="dynamic")
    wishlists = db.relationship("Wishlist", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.name}>"
