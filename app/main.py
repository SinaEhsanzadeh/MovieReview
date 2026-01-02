from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.controllers import movies
from app.db.session import engine
from app.db.base import Base
from app.exceptions.errors import NotFoundError, ValidationError


# ensure models are imported so metadata is available to Alembic/autogenerate
from app import models # noqa: F401


app = FastAPI(title="Movie Rating System API")


# include routers
app.include_router(movies.router)


# Exception handlers to return the PDF-specified error format
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"status": "error", "error": {"code": 404, "message": exc.message}})


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"status": "error", "error": {"code": 422, "message": exc.message}})


# root
@app.get("/")
async def root():
    return {"status": "ok", "message": "Movie Rating Backend is up"}


# a convenience function to create DB (for dev only)
def create_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    create_db()
    uvicorn.run(app, host="localhost", port=8000)