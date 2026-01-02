from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text
from typing import List

from app.db.base import Base

class Genre(Base):
    """Genre Model"""

    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    #many-to-many relationship between movies and genres
    movies: Mapped[List["Movie"]] = relationship("Movie", secondary="movie_genres", back_populates="genres")