from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


# association table for many-to-many
movie_genres = Table(
"movie_genres",
Base.metadata,
Column("movie_id", Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True),
Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)


class Director(Base):
    __tablename__ = "directors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    birth_year = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)


    movies = relationship("Movie", back_populates="director")


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    director_id = Column(Integer, ForeignKey("directors.id", ondelete="SET NULL"), nullable=True)
    release_year = Column(Integer, nullable=True)
    cast = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    director = relationship("Director", back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres, lazy="joined")
    ratings = relationship("MovieRating", back_populates="movie", cascade="all, delete-orphan")


class MovieRating(Base):
    __tablename__ = "movie_ratings"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False) # 1..10
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    movie = relationship("Movie", back_populates="ratings")