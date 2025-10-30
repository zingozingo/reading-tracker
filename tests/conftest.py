"""
Pytest configuration and shared fixtures

This file contains fixtures that are available to all test files.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.core.database import Base, get_db
from app.core.config import settings


# Create a test client
@pytest.fixture(scope="function")
def client():
    """
    Fixture that provides a TestClient for making requests to the API.

    Usage in tests:
        def test_something(client):
            response = client.get("/api/v1/books/")
            assert response.status_code == 200
    """
    return TestClient(app)


# Database session fixture
@pytest.fixture(scope="function")
def db_session():
    """
    Fixture that provides a database session for testing.
    Uses the same database as the app (booktracker_db).

    Note: These tests use the actual database, not a separate test database.
    Be careful with destructive operations!

    Usage in tests:
        def test_create_book(db_session):
            from app.crud import book
            new_book = book.create_book(db_session, book_data)
            assert new_book.id is not None
    """
    # Use the same database URL from settings
    engine = create_engine(settings.database_url)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create a new session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
