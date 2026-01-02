from sqlalchemy.orm import Session
from app.repositories.movie_repo import SqlAlchemyMovieRepository
from app.exceptions.errors import NotFoundError, ValidationError


class MovieService:
    def __init__(self, movie_repo: SqlAlchemyMovieRepository):
        self.repo = movie_repo


    def list_all_movies(self, page=1, page_size=10):
        total, items = self.repo.get_all(page, page_size)
        return {"page": page, "page_size": page_size, "total_items": total, "items": items}


    def get_movie(self, movie_id: int):
        m = self.repo.get_by_id(movie_id)
        if not m:
            raise NotFoundError("Movie not found")
        return m


    def create_movie(self, payload: dict):
        # validate director
        director = self.repo._get_director(payload["director_id"])
        if not director:
            raise ValidationError("Invalid director_id")


        # validate genres
        if payload.get("genres"):
            found = self.repo._get_genres(payload["genres"])
            found_count = len(found)
            if found_count != len(payload["genres"]):
                raise ValidationError("One or more genre ids are invalid")


        movie = self.repo.create(payload["title"], payload["director_id"], payload.get("release_year"), payload.get("cast"))
        if payload.get("genres"):
            self.repo.add_genres(movie, payload["genres"])

        return movie


    def add_rating(self, movie_id: int, score: int):
        movie = self.get_movie(movie_id)
        if not movie:
            raise NotFoundError("Movie not found")
        if not isinstance(score, int) or score < 1 or score > 10:
            raise ValidationError("Score must be an integer between 1 and 10")
        rating = self.repo.create_rating(movie_id, score)
        return rating