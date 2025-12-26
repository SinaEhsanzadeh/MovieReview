from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Tuple, List
from app.models.models import Movie, MovieRating, Genre, Director, movie_genres


class MovieRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_paginated(self, page: int = 1, page_size: int = 10, title: Optional[str] = None, release_year: Optional[int] = None, genre: Optional[str] = None) -> Tuple[int, List[Movie]]:
        query = self.db.query(Movie)
        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if release_year:
            query = query.filter(Movie.release_year == release_year)
        if genre:
            query = query.join(movie_genres).join(Genre).filter(Genre.name == genre)
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()


        # attach aggregates
        for m in items:
            m.ratings_count = self.db.query(func.count(MovieRating.id)).filter(MovieRating.movie_id == m.id).scalar() or 0
            avg = self.db.query(func.avg(MovieRating.score)).filter(MovieRating.movie_id == m.id).scalar()
            m.average_rating = round(float(avg), 2) if avg is not None else None
        return total, items


    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        return self.db.query(Movie).filter(Movie.id == movie_id).one_or_none()


    def create(self, title: str, director_id: int, release_year: Optional[int], cast: Optional[str]) -> Movie:
        movie = Movie(title=title, director_id=director_id, release_year=release_year, cast=cast)
        self.db.add(movie)
        self.db.flush()
        return movie


    def add_genres(self, movie: Movie, genre_ids: List[int]) -> None:
        genres = self.db.query(Genre).filter(Genre.id.in_(genre_ids)).all()
        movie.genres = genres


    def create_rating(self, movie_id: int, score: int) -> MovieRating:
        rating = MovieRating(movie_id=movie_id, score=score)
        self.db.add(rating)
        self.db.flush()
        return rating