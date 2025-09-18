from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.book import BookStatus


class BookBase(BaseModel):
    title: str = Field(..., max_length=200)
    author: str = Field(..., max_length=200)
    isbn: Optional[str] = Field(None, max_length=13)
    total_pages: int = Field(..., gt=0)
    current_page: int = Field(0, ge=0)
    status: BookStatus = BookStatus.want_to_read
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class BookCreate(BookBase):
    date_started: Optional[datetime] = None
    date_finished: Optional[datetime] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    author: Optional[str] = Field(None, max_length=200)
    isbn: Optional[str] = Field(None, max_length=13)
    total_pages: Optional[int] = Field(None, gt=0)
    current_page: Optional[int] = Field(None, ge=0)
    status: Optional[BookStatus] = None
    date_started: Optional[datetime] = None
    date_finished: Optional[datetime] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class Book(BookBase):
    id: int
    date_added: datetime
    date_started: Optional[datetime] = None
    date_finished: Optional[datetime] = None

    class Config:
        from_attributes = True