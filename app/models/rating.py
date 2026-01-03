from datetime import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

class MovieRating(Base):
    """Rating model"""

    __tablename__ = "movie_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(nullable=False) #Should be between 1 and 10
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    #one-to-many relationship between movies and ratings
    movie: Mapped["Movie"] = relationship("Movie", back_populates="ratings")
