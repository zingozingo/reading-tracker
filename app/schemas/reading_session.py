from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional
from app.schemas.book import Book


class SessionBase(BaseModel):
    start_time: datetime
    pages_read: int = Field(..., ge=0)
    notes: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    pages_read: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class Session(SessionBase):
    id: int
    book_id: int
    end_time: Optional[datetime] = None
    created_at: datetime

    @computed_field
    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate duration in minutes if end_time is set"""
        if self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None

    @computed_field
    @property
    def is_active(self) -> bool:
        """True if session is still ongoing (no end_time)"""
        return self.end_time is None

    class Config:
        from_attributes = True


class SessionWithBook(Session):
    book: Book

    class Config:
        from_attributes = True