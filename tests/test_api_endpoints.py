"""
Tests for API endpoints

These tests verify that the API endpoints return correct status codes and data.
"""

import pytest


def test_root_endpoint(client):
    """Test the root endpoint returns a welcome message"""
    # Act: Make a GET request to the root
    response = client.get("/")

    # Assert: Should return 200 OK with a message
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Book Tracker API" in response.json()["message"]


def test_health_endpoint(client):
    """Test the health check endpoint"""
    # Act: Make a GET request to /health
    response = client.get("/health")

    # Assert: Should return 200 OK with healthy status
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_book_endpoint(client):
    """Test creating a book via the API"""
    # Arrange: Prepare book data
    book_data = {
        "title": "API Test Book",
        "author": "API Test Author",
        "total_pages": 300,
        "isbn": "9876543210987"
    }

    # Act: POST to create a book
    response = client.post("/api/v1/books/", json=book_data)

    # Assert: Should return 201 Created with the created book
    assert response.status_code == 201
    created_book = response.json()
    assert created_book["title"] == "API Test Book"
    assert created_book["author"] == "API Test Author"
    assert created_book["status"] == "want_to_read"
    assert "id" in created_book

    # Cleanup: Delete the created book
    book_id = created_book["id"]
    client.delete(f"/api/v1/books/{book_id}")


def test_get_books_list_endpoint(client):
    """Test getting the list of books"""
    # Act: GET the books list
    response = client.get("/api/v1/books/")

    # Assert: Should return 200 OK with a list
    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)


def test_get_single_book_endpoint(client):
    """Test getting a single book by ID"""
    # Arrange: Create a book first
    book_data = {
        "title": "Get Single Book",
        "author": "Get Author",
        "total_pages": 200
    }
    create_response = client.post("/api/v1/books/", json=book_data)
    book_id = create_response.json()["id"]

    # Act: GET the specific book
    response = client.get(f"/api/v1/books/{book_id}")

    # Assert: Should return 200 OK with the book data
    assert response.status_code == 200
    book = response.json()
    assert book["id"] == book_id
    assert book["title"] == "Get Single Book"

    # Cleanup
    client.delete(f"/api/v1/books/{book_id}")


def test_get_nonexistent_book_endpoint(client):
    """Test that getting a non-existent book returns 404"""
    # Act: Try to GET a book that doesn't exist
    response = client.get("/api/v1/books/999999")

    # Assert: Should return 404 Not Found
    assert response.status_code == 404


def test_update_book_endpoint(client):
    """Test updating a book via the API"""
    # Arrange: Create a book first
    book_data = {
        "title": "Original API Title",
        "author": "Original API Author",
        "total_pages": 150
    }
    create_response = client.post("/api/v1/books/", json=book_data)
    book_id = create_response.json()["id"]

    # Act: PUT to update the book
    update_data = {
        "title": "Updated API Title",
        "current_page": 75,
        "status": "reading"
    }
    response = client.put(f"/api/v1/books/{book_id}", json=update_data)

    # Assert: Should return 200 OK with updated data
    assert response.status_code == 200
    updated_book = response.json()
    assert updated_book["title"] == "Updated API Title"
    assert updated_book["current_page"] == 75
    assert updated_book["status"] == "reading"

    # Cleanup
    client.delete(f"/api/v1/books/{book_id}")


def test_delete_book_endpoint(client):
    """Test deleting a book via the API"""
    # Arrange: Create a book first
    book_data = {
        "title": "Book to Delete via API",
        "author": "Delete API Author",
        "total_pages": 100
    }
    create_response = client.post("/api/v1/books/", json=book_data)
    book_id = create_response.json()["id"]

    # Act: DELETE the book
    delete_response = client.delete(f"/api/v1/books/{book_id}")

    # Assert: Should return 200 OK
    assert delete_response.status_code == 200

    # Verify the book is gone
    get_response = client.get(f"/api/v1/books/{book_id}")
    assert get_response.status_code == 404


def test_create_book_with_invalid_data(client):
    """Test that creating a book with invalid data returns 422"""
    # Arrange: Invalid data (missing required fields)
    invalid_data = {
        "title": "Only Title"
        # Missing required 'author' and 'total_pages'
    }

    # Act: Try to POST invalid data
    response = client.post("/api/v1/books/", json=invalid_data)

    # Assert: Should return 422 Unprocessable Entity
    assert response.status_code == 422


def test_book_pagination(client):
    """Test that book list pagination works"""
    # Act: GET books with limit parameter
    response = client.get("/api/v1/books/?limit=5")

    # Assert: Should return 200 OK
    assert response.status_code == 200
    books = response.json()
    assert isinstance(books, list)
    # List should have at most 5 items
    assert len(books) <= 5
