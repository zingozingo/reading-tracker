from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class BookStatus(str, enum.Enum):
    want_to_read = "want_to_read"
    reading = "reading"
    completed = "completed"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    isbn = Column(String(13), nullable=True)
    total_pages = Column(Integer, nullable=False)
    current_page = Column(Integer, default=0)
    status = Column(Enum(BookStatus), default=BookStatus.want_to_read)
    date_added = Column(DateTime(timezone=True), server_default=func.now())
    date_started = Column(DateTime(timezone=True), nullable=True)
    date_finished = Column(DateTime(timezone=True), nullable=True)
    rating = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationship
    sessions = relationship("ReadingSession", back_populates="book", cascade="all, delete-orphan")