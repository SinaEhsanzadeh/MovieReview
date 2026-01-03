from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any


class DirectorSummaryOut(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True,
        "extra": "ignore"  # Ignore extra fields from ORM object
    }


class DirectorFullInfoOut(BaseModel):
    id: int
    name: str
    birth_year: Optional[int] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class GenreOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class MovieSummaryOut(BaseModel):
    id: int
    title: str
    release_year: int = None
    director: DirectorSummaryOut = None
    genres: List[str] = []
    average_rating: Optional[float] = None
    ratings_count: int = 0

    model_config = {"from_attributes": True}

    @field_validator('genres', mode='before')
    @classmethod
    def convert_genre_to_strings(cls, v: Any) -> str:
        """Convert Genre ORM objects to strings."""
        if not v:
            return []
        if isinstance(v, list):
            # Check if first item is a Genre ORM object
            if len(v) > 0 and hasattr(v[0], 'name'):
                return [g.name for g in v]
            # Already strings or empty
            return v
        return []


class MovieFullInfoOut(BaseModel):
    id: int
    title: str
    release_year: int = None
    director: DirectorFullInfoOut = None
    genres: List[str] = []
    cast: str
    average_rating: Optional[float] = None
    ratings_count: int = 0

    model_config = {"from_attributes": True}

    @field_validator('genres', mode='before')
    @classmethod
    def convert_genres_to_strings(cls, v: Any) -> List[str]:
        """Convert Genre ORM objects to strings."""
        if not v:
            return []
        if isinstance(v, list):
            # Check if first item is a Genre ORM object
            if len(v) > 0 and hasattr(v[0], 'name'):
                return [g.name for g in v]
            # Already strings or empty
            return v
        return []


class MovieListItem(BaseModel):
    status: str
    page: int
    page_size: int
    total_items: int
    data: List[MovieSummaryOut]


class MovieSingleItem(BaseModel):
    status: str
    data: List[MovieFullInfoOut]


class MovieCreate(BaseModel):
    title: str
    director_id: int
    release_year: int = Field(..., ge=1850, le=2026, description="Release year must be between 1850 and current year=2026")
    cast: Optional[str] = None
    genres: List[int] = []


class RatingCreate(BaseModel):
    score: int = Field(..., ge=1, le=10)


    @field_validator("score")
    def must_be_int(cls, v):
        if not isinstance(v, int):
            raise ValueError("Score must be an integer between 1 and 10")
        return v