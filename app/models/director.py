from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text
from typing import List

from app.db.base import Base

class Director(Base):
    """director model"""

    __tablename__ = "directors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_year: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    #one-to-many relationship between directors and movies
    movies: Mapped[List["Movie"]] = relationship("Movie", back_populates="director") 