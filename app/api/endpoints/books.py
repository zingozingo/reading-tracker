from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.crud import book as crud_book
from app.schemas.book import Book, BookCreate, BookUpdate
from app.models.book import BookStatus

router = APIRouter()


@router.get("/", response_model=List[Book])
def read_books(
    skip: int = 0,
    limit: int = 100,
    status: Optional[BookStatus] = None,
    db: Session = Depends(get_db)
):
    books = crud_book.get_books(db, skip=skip, limit=limit, status=status)
    return books


@router.get("/{book_id}", response_model=Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud_book.get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.post("/", response_model=Book, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return crud_book.create_book(db=db, book=book)


@router.put("/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = crud_book.update_book(db, book_id=book_id, book=book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@router.delete("/{book_id}", response_model=Book)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = crud_book.delete_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book