from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class DirectorOut(BaseModel):
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None


    class Config:
        orm_mode = True


class MovieListItem(BaseModel):
    id: int
    title: str
    release_year: Optional[int] = None
    director: Optional[DirectorOut] = None
    genres: List[str] = []
    average_rating: Optional[float] = None
    ratings_count: int = 0


    class Config:
        orm_mode = True


class MovieCreate(BaseModel):
    title: str
    director_id: int
    release_year: Optional[int]
    cast: Optional[str] = None
    genres: List[int] = []


class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)


    @field_validator("score")
    def must_be_int(cls, v):
        if not isinstance(v, int):
            raise ValueError("Score must be an integer between 1 and 10")
        return v