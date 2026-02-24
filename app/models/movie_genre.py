from app.extensions import db


movie_genres = db.Table(
    "movie_genres",
    db.Column("movie_id", db.UUID, db.ForeignKey("movies.id"), primary_key=True),
    db.Column("genre_id", db.UUID, db.ForeignKey("genres.id"), primary_key=True),
)
