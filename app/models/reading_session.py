from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ReadingSession(Base):
    __tablename__ = "reading_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    pages_read = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    book = relationship("Book", back_populates="sessions")