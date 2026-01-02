from typing import Optional
from sqlalchemy.orm import Session
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
    def get_all(self, page: int = 1, page_size: int = 10) -> List[Movie]:
        ...
    def get_filtered(self, page: int = 1, page_size: int = 10, title: Optional[str] = None, release_year: Optional[int] = None, genre: Optional[str] = None) -> List[Movie]:
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
        query = self.db.query(Movie) #return all movies
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
            m.ratings_count = self.__get_ratings_count(m.id)
            avg = self.__get_average_rating(m.id)
            m.average_rating = round(avg, 2) if avg is not None else None
        return total, items #returns total-count and list of all movies of current page, using tuple




    def get_all(self, page: int = 1, page_size: int = 10) -> List[Movie]:
        return self.__get_paginated(page, page_size, None, None, None)

    
    def get_by_id(self, movie_id: int) -> Optional[Movie]:
        fully_detailed_movie = self.db.query(Movie).filter(Movie.id == movie_id).one_or_none()
        if not fully_detailed_movie:
            raise NotFoundError("Movie not found. Invalid id.")
        fully_detailed_movie.ratings_count = self.__get_ratings_count(movie_id)
        avg = self.__get_average_rating(movie_id)
        fully_detailed_movie.average_rating = round(avg, 2) if avg is not None else None
        return fully_detailed_movie


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