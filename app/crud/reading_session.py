from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.models.reading_session import ReadingSession
from app.models.book import Book, BookStatus
from app.schemas.reading_session import SessionCreate, SessionUpdate
from datetime import datetime
from typing import Optional


def create_session(db: Session, book_id: int, session_data: SessionCreate):
    """Create a new reading session and update book progress"""
    # Get the book
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return None
    
    # Create the session
    db_session = ReadingSession(
        book_id=book_id,
        **session_data.model_dump()
    )
    db.add(db_session)
    
    # Update book progress
    book.current_page += session_data.pages_read
    
    # Update book status logic
    if book.status == BookStatus.want_to_read:
        book.status = BookStatus.reading
        if not book.date_started:
            book.date_started = session_data.start_time
    
    # Check if book is completed
    if book.current_page >= book.total_pages:
        book.status = BookStatus.completed
        if not book.date_finished:
            book.date_finished = session_data.start_time
    
    db.commit()
    db.refresh(db_session)
    return db_session


def get_sessions_for_book(db: Session, book_id: int, skip: int = 0, limit: int = 100):
    """Get all reading sessions for a specific book"""
    return db.query(ReadingSession).filter(
        ReadingSession.book_id == book_id
    ).offset(skip).limit(limit).all()


def get_session(db: Session, session_id: int):
    """Get a specific reading session"""
    return db.query(ReadingSession).filter(ReadingSession.id == session_id).first()


def end_session(db: Session, session_id: int, end_time: Optional[datetime] = None):
    """End a reading session by setting the end_time"""
    db_session = db.query(ReadingSession).filter(ReadingSession.id == session_id).first()
    if db_session and db_session.end_time is None:
        db_session.end_time = end_time or datetime.now()
        db.commit()
        db.refresh(db_session)
    return db_session


def update_session(db: Session, session_id: int, session_update: SessionUpdate):
    """Update a reading session"""
    db_session = db.query(ReadingSession).filter(ReadingSession.id == session_id).first()
    if db_session:
        update_data = session_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_session, field, value)
        db.commit()
        db.refresh(db_session)
    return db_session


def get_all_sessions(db: Session, skip: int = 0, limit: int = 100):
    """Get all reading sessions across all books"""
    return db.query(ReadingSession).offset(skip).limit(limit).all()


def get_active_sessions(db: Session, book_id: Optional[int] = None):
    """Get all active (ongoing) reading sessions"""
    query = db.query(ReadingSession).filter(ReadingSession.end_time.is_(None))
    if book_id:
        query = query.filter(ReadingSession.book_id == book_id)
    return query.all()