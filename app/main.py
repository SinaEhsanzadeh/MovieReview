from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.controllers import movies
from app.db.session import engine
from app.db.base import Base
from app.exceptions.errors import NotFoundError, ValidationError
import logging

from app.logging_config import setup_logging

from app import models # noqa: F401

setup_logging()
logger = logging.getLogger("movie_rating")

app = FastAPI(title="Movie Rating System API")


app.include_router(movies.router)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    logger.error(f"Resource not found: {exc.message}")
    return JSONResponse(status_code=404, content={"status": "error", "error": {"code": 404, "message": exc.message}})


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(status_code=422, content={"status": "error", "error": {"code": 422, "message": exc.message}})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}", exc_info=True)
        raise

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"status": "ok", "message": "Movie Rating Backend is up"}

def create_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    create_db()
    uvicorn.run(app, host="localhost", port=8000)