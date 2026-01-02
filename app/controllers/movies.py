from fastapi import APIRouter, Depends, HTTPException, status
from typing import  Annotated

from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.services.movie_service import MovieService
from app.repositories.movie_repo import SqlAlchemyMovieRepository
from app.schemas.movie import MovieCreate, RatingCreate
from app.exceptions.errors import NotFoundError, ValidationError


router = APIRouter(prefix="/api/v1/movies", tags=["movies"])


# dependency
def get_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> MovieService:
    repository = SqlAlchemyMovieRepository(session)
    return MovieService(repository)


@router.get("/")
def list_all_movies(page: int = 1, page_size: int = 10, movie_service: MovieService = Depends(get_service)): 
    res = movie_service.list_all_movies(page=page, page_size=page_size)
    # transform ORM objects to simple dicts for JSON serialization
    items = []
    for m in res["items"]:
        items.append({
            "id": m.id,
            "title": m.title,
            "release_year": m.release_year,
            "director": {"id": m.director.id, "name": m.director.name} if m.director else None,
            "genres": [g.name for g in m.genres],
            "average_rating": getattr(m, "average_rating", None),
            "ratings_count": getattr(m, "ratings_count", 0),
        })
    return {"status": "success", "data": {"page": res["page"], "page_size": res["page_size"], "total_items": res["total_items"], "items": items}}


@router.get("/{movie_id}")
def get_movie(movie_id: int, movie_service: MovieService = Depends(get_service)):
    try:
        m = movie_service.get_movie(movie_id)
        if not m:
            raise NotFoundError()
        return {"status": "success", "data": {
            "id": m.id,
            "title": m.title,
            "release_year": m.release_year,
            "director": {"id": m.director.id, "name": m.director.name, "birth_year": m.director.birth_year, "description": m.director.description} if m.director else None,
            "genres": [g.name for g in m.genres],
            "cast": m.cast,
            "average_rating": m.average_rating,
            "ratings_count": m.ratings_count
        }}
    except NotFoundError:
        raise HTTPException(status_code=404, detail={"code":404, "message":"Movie not found"})


@router.post("/", status_code=201)
def create_movie(payload: MovieCreate, movie_service: MovieService = Depends(get_service)):
    try:
        m = movie_service.create_movie(payload.dict())
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"code":422, "message": e.message})

    return {"status": "success", "data": {
            "id": m.id,
            "title": m.title,
            "release_year": m.release_year,
            "director": {"id": m.director.id, "name": m.director.name} if m.director else None,
            "genres": [g.name for g in m.genres],
            "cast": m.cast,
            "average_rating": None,
            "ratings_count": 0
        }}


@router.post("/{movie_id}/ratings", status_code=201)
def add_rating(movie_id: int, payload: RatingCreate, movie_service: MovieService = Depends(get_service)):
    try:
        rating = movie_service.add_rating(movie_id, payload.score)
    except NotFoundError:
        raise HTTPException(status_code=404, detail={"code": 404, "message": "Movie not found"})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"code": 422, "message": e.message})

    return {"status": "success", "data": {"rating_id": rating.id, "movie_id": movie_id, "score": rating.score}, "created_at": rating.created_at.isoformat()}
