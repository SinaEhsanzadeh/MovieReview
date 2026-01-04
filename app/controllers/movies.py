from fastapi import status
from fastapi.responses import Response
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Optional, List
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db_session
from app.services.movie_service import MovieService
from app.repositories.movie_repo import SqlAlchemyMovieRepository
from app.schemas.movie import MovieCreate, RatingCreate, MovieListItem, MovieSummaryOut, MovieFullInfoOut, MovieSingleItem
from app.exceptions.errors import NotFoundError, ValidationError

router = APIRouter(prefix="/api/v1/movies", tags=["movies"])

logger = logging.getLogger("movie_rating")

def get_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> MovieService:
    repository = SqlAlchemyMovieRepository(session)
    return MovieService(repository)


@router.get("/", response_model=MovieListItem)
def list_all_movies_with_query_params(
        page: int = 1,
        page_size: int = 10,
        movie_service: MovieService = Depends(get_service),
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        genre: Optional[str] = None
):
    logger.info(
        f"GET movies list - page={page}, page_size={page_size}, "
        f"title={title}, release_year={release_year}, genre={genre}"
    )

    try:
        res = movie_service.filter_movies(page, page_size, title, release_year, genre)

        # Convert ORM objects to Pydantic models
        movie_items = [MovieSummaryOut.model_validate(m) for m in res["items"]]

        # Log successful response
        logger.info(
            f"Movies list retrieved successfully - "
            f"page={res['page']}, total_items={res['total_items']}, "
            f"items_count={len(movie_items)}"
        )

        return MovieListItem(
            status="success",
            page=res["page"],
            page_size=res["page_size"],
            total_items=res["total_items"],
            data=movie_items
        )
    except Exception as e:
        logger.error(f"Error retrieving movies list: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": 500, "message": "Internal server error"})


@router.get("/{movie_id}", response_model=MovieSingleItem)
def get_movie_by_id(movie_id: int, movie_service: MovieService = Depends(get_service)):
    logger.info(f"GET movie details - movie_id={movie_id}")

    try:
        m = movie_service.get_movie(movie_id)
        if not m:
            logger.warning(f"Movie not found - movie_id={movie_id}")
            raise NotFoundError()

        movie = MovieFullInfoOut.model_validate(m)
        logger.info(f"Movie details retrieved - movie_id={movie_id}, title={movie.title}")

        return MovieSingleItem(
            status="success",
            data=[movie]
        )
    except NotFoundError:
        logger.warning(f"Movie not found for GET request - movie_id={movie_id}")
        raise HTTPException(status_code=404, detail={"code": 404, "message": "Movie not found"})
    except Exception as e:
        logger.error(f"Error getting movie details - movie_id={movie_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": 500, "message": "Internal server error"})


@router.post("/", status_code=201, response_model=MovieSingleItem)
def create_movie(payload: MovieCreate, movie_service: MovieService = Depends(get_service)):
    logger.info(f"POST create movie - title={payload.title}, director_id={payload.director_id}")

    try:
        m = movie_service.create_movie(payload.dict())
    except ValidationError as e:
        logger.warning(f"Validation error creating movie - {e.message}")
        raise HTTPException(status_code=422, detail={"code": 422, "message": e.message})
    except Exception as e:
        logger.error(f"Error creating movie: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": 500, "message": "Internal server error"})

    movie = MovieFullInfoOut.model_validate(m)
    logger.info(f"Movie created successfully - movie_id={movie.id}, title={movie.title}")

    return MovieSingleItem(
        status="success",
        data=[movie]
    )


@router.post("/{movie_id}/ratings", status_code=201)
def add_rating_to_a_movie(movie_id: int, payload: RatingCreate, movie_service: MovieService = Depends(get_service)):
    # Log the rating attempt with context (as per PDF example)
    logger.info(f"Rating movie - movie_id={movie_id}, rating={payload.score}, route=/api/v1/movies/{movie_id}/ratings")

    try:
        rating = movie_service.add_rating(movie_id, payload.score)

        # Check if rating is valid (1-10)
        if payload.score < 1 or payload.score > 10:
            logger.warning(f"Invalid rating value - movie_id={movie_id}, rating={payload.score}")
            raise ValidationError("Score must be between 1 and 10")

    except NotFoundError:
        logger.warning(f"Movie not found for rating - movie_id={movie_id}")
        raise HTTPException(status_code=404, detail={"code": 404, "message": "Movie not found"})
    except ValidationError as e:
        logger.warning(f"Invalid rating - movie_id={movie_id}, rating={payload.score}: {e.message}")
        raise HTTPException(status_code=422, detail={"code": 422, "message": e.message})
    except Exception as e:
        # Log database/saving errors as ERROR (as per PDF example)
        logger.error(f"Failed to save rating - movie_id={movie_id}, rating={payload.score}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": 500, "message": "Internal server error"})

    # Log successful rating creation (as per PDF example)
    logger.info(f"Rating saved successfully - movie_id={movie_id}, rating={payload.score}")

    return {
        "status": "success",
        "data": {
            "rating_id": rating.id,
            "movie_id": movie_id,
            "score": rating.score
        },
        "created_at": rating.created_at.isoformat()
    }


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_movie_by_id(movie_id: int, movie_service: MovieService = Depends(get_service)):
    logger.info(f"DELETE movie - movie_id={movie_id}")

    try:
        movie_service.remove_movie(movie_id)
        logger.info(f"Movie deleted successfully - movie_id={movie_id}")
    except NotFoundError:
        logger.warning(f"Movie not found for deletion - movie_id={movie_id}")
        raise HTTPException(status_code=404, detail={"code": 404, "message": "Movie not found"})
    except Exception as e:
        logger.error(f"Error deleting movie - movie_id={movie_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": 500, "message": "Internal server error"})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{movie_id}", response_model=MovieSingleItem)
def update_movie_by_id(
        movie_id: int,
        payload: MovieCreate,
        movie_service: MovieService = Depends(get_service)
):
    logger.info(f"PUT update movie - movie_id={movie_id}")

    try:
        m = movie_service.update_movie(movie_id, payload.dict())
    except NotFoundError:
        logger.warning(f"Movie not found for update - movie_id={movie_id}")
        raise HTTPException(status_code=404, detail={"code": 404, "message": "Movie not found"})
    except ValidationError as e:
        logger.warning(f"Validation error updating movie - movie_id={movie_id}: {e.message}")
        raise HTTPException(status_code=422, detail={"code": 422, "message": e.message})
    except Exception as e:
        logger.error(f"Error updating movie - movie_id={movie_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={"code": 500, "message": "Internal server error"})

    movie = MovieFullInfoOut.model_validate(m)
    logger.info(f"Movie updated successfully - movie_id={movie_id}, title={movie.title}")

    return MovieSingleItem(
        status="success",
        data=[movie]
    )