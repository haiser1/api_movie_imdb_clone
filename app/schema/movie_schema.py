"""Pydantic schemas for movie validation and serialization."""

from uuid import UUID
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class MovieCreateSchema(BaseModel):
    """Schema for user-created movie."""

    title: str = Field(..., max_length=255)
    overview: Optional[str] = None
    release_date: Optional[date] = None
    genre_ids: Optional[List[str]] = None


class MovieUpdateSchema(BaseModel):
    """Schema for updating a user movie."""

    title: Optional[str] = Field(None, max_length=255)
    overview: Optional[str] = None
    release_date: Optional[date] = None
    genre_ids: Optional[List[str]] = None


class AdminMovieCreateSchema(BaseModel):
    """Schema for admin-created movie (extra fields)."""

    title: str = Field(..., max_length=255)
    overview: Optional[str] = None
    release_date: Optional[date] = None
    popularity: Optional[float] = None
    rating: Optional[float] = None
    is_featured: Optional[bool] = False
    status: Optional[str] = "active"
    genre_ids: Optional[List[UUID]] = None


class AdminMovieUpdateSchema(BaseModel):
    """Schema for admin movie update."""

    title: Optional[str] = Field(None, max_length=255)
    overview: Optional[str] = None
    release_date: Optional[date] = None
    popularity: Optional[float] = None
    rating: Optional[float] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None
    genre_ids: Optional[List[str]] = None


def serialize_movie(movie):
    """Serialize a Movie model instance to dict.

    Args:
        movie: Movie model instance with loaded relationships.

    Returns:
        dict with movie data including genres, images, and videos.
    """
    return {
        "id": str(movie.id),
        "api_id": movie.api_id,
        "source": movie.source,
        "title": movie.title,
        "overview": movie.overview,
        "release_date": movie.release_date.isoformat() if movie.release_date else None,
        "popularity": movie.popularity,
        "rating": movie.rating,
        "is_featured": movie.is_featured,
        "status": movie.status,
        "created_by": str(movie.created_by) if movie.created_by else None,
        "genres": [{"id": str(g.id), "name": g.name} for g in movie.genres],
        "images": [
            {
                "id": str(img.id),
                "image_type": img.image_type,
                "image_url": img.image_url,
                "width": img.width,
                "height": img.height,
            }
            for img in movie.images
        ],
        "videos": [
            {
                "id": str(v.id),
                "video_type": v.video_type,
                "site": v.site,
                "video_key": v.video_key,
                "official": v.official,
            }
            for v in movie.videos
        ],
        "created_at": movie.created_at.isoformat() if movie.created_at else None,
        "updated_at": movie.updated_at.isoformat() if movie.updated_at else None,
    }
