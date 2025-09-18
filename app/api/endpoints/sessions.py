from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.crud import reading_session as crud_session
from app.crud import book as crud_book
from app.schemas.reading_session import Session as SessionSchema, SessionCreate, SessionUpdate, SessionWithBook

router = APIRouter()


@router.post("/books/{book_id}/sessions", response_model=SessionSchema, status_code=201)
def create_reading_session(
    book_id: int,
    session: SessionCreate,
    db: Session = Depends(get_db)
):
    """Start a new reading session for a book"""
    # Check if book exists
    book = crud_book.get_book(db, book_id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_session = crud_session.create_session(db=db, book_id=book_id, session_data=session)
    return db_session


@router.get("/books/{book_id}/sessions", response_model=List[SessionSchema])
def get_book_sessions(
    book_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all reading sessions for a specific book"""
    # Check if book exists
    book = crud_book.get_book(db, book_id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    sessions = crud_session.get_sessions_for_book(db, book_id=book_id, skip=skip, limit=limit)
    return sessions


@router.get("/sessions", response_model=List[SessionWithBook])
def get_all_sessions(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all reading sessions across all books"""
    if active_only:
        sessions = crud_session.get_active_sessions(db)
    else:
        sessions = crud_session.get_all_sessions(db, skip=skip, limit=limit)
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionWithBook)
def get_reading_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific reading session"""
    db_session = crud_session.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Reading session not found")
    return db_session


@router.put("/sessions/{session_id}/end", response_model=SessionSchema)
def end_reading_session(
    session_id: int,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """End a reading session"""
    db_session = crud_session.end_session(db, session_id=session_id, end_time=end_time)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Reading session not found or already ended")
    return db_session


@router.put("/sessions/{session_id}", response_model=SessionSchema)
def update_reading_session(
    session_id: int,
    session_update: SessionUpdate,
    db: Session = Depends(get_db)
):
    """Update a reading session"""
    db_session = crud_session.update_session(db, session_id=session_id, session_update=session_update)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Reading session not found")
    return db_session