from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Table, Column, Integer, Text

from app.db.base import Base

# association table for many-to-many relationship between movies and genres
movie_genres = Table(
    "movie_genres",
    Base.metadata,
    #Making a composite primary key
    Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)
)

class Movie(Base):
    """Movie model"""

    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    director_id: Mapped[int] = mapped_column(ForeignKey("directors.id", ondelete="RESTRICT"), nullable=False)
    release_year: Mapped[int] = mapped_column(nullable=False)
    cast: Mapped[str] = mapped_column(Text, nullable=True)

    #one-to-many relationship between directors and movies
    director: Mapped["Director"] = relationship("Director", back_populates="movies")
    #many-to-many relationship between movies and genres
    genres: Mapped[List["Genre"]] = relationship("Genre", secondary="movie_genres", back_populates="movies")
    #one-to-many relationship between movies and ratings
    ratings: Mapped[List["MovieRating"]] = relationship("MovieRating", back_populates="movie", cascade="all, delete-orphan")


