from fastapi import status
from fastapi.responses import Response

from fastapi import APIRouter, Depends, HTTPException
from typing import  Annotated, Optional, List

from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.movie_service import MovieService
from app.repositories.movie_repo import SqlAlchemyMovieRepository
from app.schemas.movie import MovieCreate, RatingCreate, MovieListItem, MovieSummaryOut, MovieFullInfoOut, MovieSingleItem
from app.exceptions.errors import NotFoundError, ValidationError


router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


# dependency
def get_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> MovieService:
    repository = SqlAlchemyMovieRepository(session)
    return MovieService(repository)


@router.get("/", response_model=MovieListItem)
def list_all_movies_with_query_params(page: int = 1, page_size: int = 10, movie_service: MovieService = Depends(get_service),
                                        title: Optional[str] = None, release_year: Optional[int] = None, genre: Optional[str] = None):
    res = movie_service.filter_movies(page, page_size, title, release_year, genre)

    # Convert ORM objects to Pydantic models - schema handles genre conversion automatically
    movie_items = [MovieSummaryOut.model_validate(m) for m in res["items"]]

    return MovieListItem(
        status="success",
        page=res["page"],
        page_size=res["page_size"],
        total_items=res["total_items"],
        data=movie_items
    )


@router.get("/{movie_id}", response_model=MovieSingleItem)
def get_movie_by_id(movie_id: int, movie_service: MovieService = Depends(get_service)):
    try:
        m = movie_service.get_movie(movie_id)
        if not m:
            raise NotFoundError()
        movie = MovieFullInfoOut.model_validate(m)
        return MovieSingleItem(
            status="success",
            data=[movie]
        )
    except NotFoundError:
        raise HTTPException(status_code=404, detail={"code":404, "message":"Movie not found"})


@router.post("/", status_code=201, response_model=MovieSingleItem)
def create_movie(payload: MovieCreate, movie_service: MovieService = Depends(get_service)):
    try:
        m = movie_service.create_movie(payload.dict())
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"code":422, "message": e.message})

    movie = MovieFullInfoOut.model_validate(m)
    return MovieSingleItem(
        status="success",
        data=[movie]
    )


@router.post("/{movie_id}/ratings", status_code=201)
def add_rating_to_a_movie(movie_id: int, payload: RatingCreate, movie_service: MovieService = Depends(get_service)):
    try:
        rating = movie_service.add_rating(movie_id, payload.score)
    except NotFoundError:
        raise HTTPException(status_code=404, detail={"code": 404, "message": "Movie not found"})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"code": 422, "message": e.message})

    return {"status": "success", "data": {"rating_id": rating.id, "movie_id": movie_id, "score": rating.score}, "created_at": rating.created_at.isoformat()}
