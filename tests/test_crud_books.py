"""
Tests for Book CRUD operations

These tests verify that book creation, reading, updating, and deletion work correctly.
"""

import pytest
from app.crud import book as crud_book
from app.schemas.book import BookCreate, BookUpdate


def test_create_book(db_session):
    """Test creating a new book"""
    # Arrange: Prepare test data
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        isbn="1234567890123",
        total_pages=300
    )

    # Act: Create the book
    created_book = crud_book.create_book(db_session, book_data)

    # Assert: Verify the book was created correctly
    assert created_book.id is not None
    assert created_book.title == "Test Book"
    assert created_book.author == "Test Author"
    assert created_book.isbn == "1234567890123"
    assert created_book.total_pages == 300
    assert created_book.current_page == 0
    assert created_book.status == "want_to_read"

    # Cleanup: Delete the test book
    crud_book.delete_book(db_session, created_book.id)


def test_get_book(db_session):
    """Test retrieving a book by ID"""
    # Arrange: Create a test book first
    book_data = BookCreate(
        title="Get Test Book",
        author="Get Test Author",
        total_pages=250
    )
    created_book = crud_book.create_book(db_session, book_data)

    # Act: Retrieve the book
    retrieved_book = crud_book.get_book(db_session, created_book.id)

    # Assert: Verify we got the correct book
    assert retrieved_book is not None
    assert retrieved_book.id == created_book.id
    assert retrieved_book.title == "Get Test Book"
    assert retrieved_book.author == "Get Test Author"

    # Cleanup
    crud_book.delete_book(db_session, created_book.id)


def test_get_nonexistent_book(db_session):
    """Test that getting a non-existent book returns None"""
    # Act: Try to get a book with an ID that doesn't exist
    book = crud_book.get_book(db_session, book_id=999999)

    # Assert: Should return None
    assert book is None


def test_update_book(db_session):
    """Test updating a book's information"""
    # Arrange: Create a test book
    book_data = BookCreate(
        title="Original Title",
        author="Original Author",
        total_pages=200
    )
    created_book = crud_book.create_book(db_session, book_data)

    # Act: Update the book
    update_data = BookUpdate(
        title="Updated Title",
        current_page=50,
        rating=4
    )
    updated_book = crud_book.update_book(db_session, created_book.id, update_data)

    # Assert: Verify the updates were applied
    assert updated_book.title == "Updated Title"
    assert updated_book.author == "Original Author"  # Unchanged
    assert updated_book.current_page == 50
    assert updated_book.rating == 4

    # Cleanup
    crud_book.delete_book(db_session, created_book.id)


def test_delete_book(db_session):
    """Test deleting a book"""
    # Arrange: Create a test book
    book_data = BookCreate(
        title="Book to Delete",
        author="Delete Author",
        total_pages=100
    )
    created_book = crud_book.create_book(db_session, book_data)
    book_id = created_book.id

    # Act: Delete the book
    result = crud_book.delete_book(db_session, book_id)

    # Assert: Verify deletion returned the deleted book
    assert result is not None
    assert result.id == book_id

    # Verify the book is actually gone
    deleted_book = crud_book.get_book(db_session, book_id)
    assert deleted_book is None


def test_book_status_transition(db_session):
    """Test that book status can transition from want_to_read to reading to completed"""
    # Arrange: Create a book
    book_data = BookCreate(
        title="Status Test Book",
        author="Status Author",
        total_pages=100
    )
    created_book = crud_book.create_book(db_session, book_data)

    # Assert: Initial status is want_to_read
    assert created_book.status == "want_to_read"

    # Act & Assert: Update to reading
    update_reading = BookUpdate(status="reading", current_page=10)
    updated_book = crud_book.update_book(db_session, created_book.id, update_reading)
    assert updated_book.status == "reading"
    assert updated_book.current_page == 10

    # Act & Assert: Update to completed
    update_completed = BookUpdate(status="completed", current_page=100)
    completed_book = crud_book.update_book(db_session, created_book.id, update_completed)
    assert completed_book.status == "completed"
    assert completed_book.current_page == 100

    # Cleanup
    crud_book.delete_book(db_session, created_book.id)
