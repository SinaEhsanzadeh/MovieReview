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
def list_movies(page: int = 1, page_size: int = 10, title: str = None, release_year: int = None, genre: str = None, db: Session = Depends(get_db)):
    svc = MovieService(db)
    res = svc.list_movies(page=page, page_size=page_size, title=title, release_year=release_year, genre=genre)
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
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    svc = MovieService(db)
    try:
        m = svc.repo.get_by_id(movie_id)
        if not m:
            raise NotFoundError()
        # compute aggregates
        from sqlalchemy import func
        ratings_count = db.query(func.count).filter_by(column=None)
        # simpler: compute with SQL
        ratings_count = db.query(func.count).filter_by
        # We'll compute directly instead of overcomplicating here
        from sqlalchemy import func
        ratings_count = db.query(func.count).filter(func.true())
        # Build response (safe fields)
        avg = db.query(func.avg)
        return {"status": "success", "data": {
            "id": m.id,
            "title": m.title,
            "release_year": m.release_year,
            "director": {"id": m.director.id, "name": m.director.name} if m.director else None,
            "genres": [g.name for g in m.genres],
            # later compute average and count
        }}
    except NotFoundError:
        raise HTTPException(status_code=404, detail={"code":404, "message":"Movie not found"})


@router.post("/", status_code=201)
def create_movie(payload: MovieCreate, db: Session = Depends(get_db)):
    svc = MovieService(db)
    try:
        movie = svc.create_movie(payload.dict())
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"code":422, "message": e.message})


    return {"status": "success", "data": {"id": movie.id, "title": movie.title}}


@router.post("/{movie_id}/ratings", status_code=201)
def add_rating(movie_id: int, payload: RatingCreate, db: Session = Depends(get_db)):
    svc = MovieService(db)
    try:
        rating = svc.add_rating(movie_id, payload.score)
    except NotFoundError:
        raise HTTPException(status_code=404, detail={"code": 404, "message": "Movie not found"})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"code": 422, "message": e.message})

    return {"status": "success", "data": {"rating_id": rating.id, "movie_id": movie_id, "score": rating.score, "created_at": rating.created_at.isoformat()}}
