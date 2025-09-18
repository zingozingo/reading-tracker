from sqlalchemy.orm import Session
from app.models.book import Book, BookStatus
from app.schemas.book import BookCreate, BookUpdate
from typing import Optional


def get_book(db: Session, book_id: int):
    return db.query(Book).filter(Book.id == book_id).first()


def get_books(db: Session, skip: int = 0, limit: int = 100, status: Optional[BookStatus] = None):
    query = db.query(Book)
    if status:
        query = query.filter(Book.status == status)
    return query.offset(skip).limit(limit).all()


def create_book(db: Session, book: BookCreate):
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book: BookUpdate):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book:
        update_data = book.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_book, field, value)
        db.commit()
        db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book