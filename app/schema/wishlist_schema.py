"""Pydantic schemas for wishlist validation."""

from datetime import date
from typing import Optional
from pydantic import BaseModel


class WishlistCreateSchema(BaseModel):
    """Schema for adding a movie to wishlist."""

    movie_id: str
    scheduled_watch_date: Optional[date] = None


class WishlistUpdateSchema(BaseModel):
    """Schema for updating a wishlist item."""

    scheduled_watch_date: Optional[date] = None
