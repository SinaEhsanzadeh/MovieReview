from typing import Optional
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import Optional, Tuple, List, Protocol

from app.models import Movie, MovieRating, Genre, Director
from app.exceptions.errors import NotFoundError


class MovieRepository(Protocol):
    def __get_paginated(self, page: int = 1, page_size: int = 10, title: Optional[str] = None, release_year: Optional[int] = None, genre: Optional[str] = None) -> Tuple[int, List[Movie]]:
        ...
    def __get_ratings_count(self, movie_id: int) -> int:
        ...
    def __get_average_count(self, movie_id: int) -> int:
        ...
    def _get_director(self, director_id: int) -> Optional[Director]:
        ...
    def _get_genres(self, genres: List[Genre]) -> Optional[List[Genre]]:
        ...
    def get_all(self, page: int = 1, page_size: int = 10) -> Tuple[int, List[Movie]]:
        ...
    def get_filtered(self, page: int = 1, page_size: int = 10, title: Optional[str] = None, release_year: Optional[int] = None, genre: Optional[str] = None) -> Tuple[int, List[Movie]]:
        ...
    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        ...
    def create(self, title: str, director_id: int, release_year: int, cast: Optional[str]) -> Movie:
        ...
    def add_genres(self, movie: Movie, genre_ids: List[int]) -> None:
        ...
    def delete(self, movie_id: int) -> None:
        ...
    def update(self, movie_id: int, title: str, director_id: int, release_year: int, cast: Optional[str]) -> Movie:
        ...
    def create_rating(self, movie_id: int, score: int) -> MovieRating:
        ...


class SqlAlchemyMovieRepository(MovieRepository):
    def __init__(self, db: Session):
        self.db = db


    def __get_ratings_count(self, movie_id: int) -> int:
        ratings_count: int = self.db.query(func.count(MovieRating.id)).filter(MovieRating.movie_id == movie_id).scalar() or 0
        return ratings_count


    def __get_average_rating(self, movie_id: int) -> int:
        average_rating: int = self.db.query(func.avg(MovieRating.score)).filter(MovieRating.movie_id == movie_id).scalar()
        return average_rating


    def __get_paginated(self, page: int = 1, page_size: int = 10, title: Optional[str] = None, release_year: Optional[int] = None, genre: Optional[str] = None) -> Tuple[int, List[Movie]]:
        query = self.db.query(Movie).options(selectinload(Movie.genres))

        if title:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if release_year:
            query = query.filter(Movie.release_year == release_year)
        if genre:
            # safest approach — uses EXISTS under the hood, no duplicate join
            query = query.filter(Movie.genres.any(Genre.name == genre))

        # total: if you had joins that could produce duplicates, use distinct:
        total = query.distinct().count()

        items = query.offset((page - 1) * page_size).limit(page_size).all()

        for m in items:
            m.ratings_count = self.__get_ratings_count(m.id)
            avg = self.__get_average_rating(m.id)
            m.average_rating = round(avg, 2) if avg is not None else None
        return total, items #returns total-count and list of all movies of current page, using tuple


    def _get_director(self, director_id: int) -> Optional[Director]:
        return self.db.query(Director).filter(Director.id == director_id).one_or_none()


    def _get_genres(self, genres: List[Genre]) -> Optional[List[Genre]]:
        return self.db.query(Genre).filter(Genre.id.in_(genres)).all()


    def get_filtered(self, page: int = 1, page_size: int = 10, title: Optional[str] = None, release_year: Optional[int] = None, genre: Optional[str] = None) -> Tuple[int, List[Movie]]:
        return self.__get_paginated(page, page_size, title, release_year, genre)


    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        fully_detailed_movie = self.db.query(Movie).filter(Movie.id == movie_id).one_or_none()
        if not fully_detailed_movie:
            raise NotFoundError("Movie not found. Invalid id.")
        fully_detailed_movie.ratings_count = self.__get_ratings_count(movie_id)
        avg = self.__get_average_rating(movie_id)
        fully_detailed_movie.average_rating = round(avg, 2) if avg is not None else None
        return fully_detailed_movie


    def create(self, title: str, director_id: int, release_year: int, cast: Optional[str]) -> Movie:
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

    def delete(self, movie: Movie) -> None:
        self.db.delete(movie)
        self.db.flush()
        return 
        
    def update(self, updated_movie: Movie) -> Movie:
        orm_movie = self.db.query(Movie).filter(Movie.id == updated_movie.id).one_or_none()
        orm_movie.title = updated_movie.title
        orm_movie.release_year = updated_movie.release_year
        orm_movie.genres = updated_movie.genres
        orm_movie.cast = updated_movie.cast
        self.db.commit()
        return orm_movie