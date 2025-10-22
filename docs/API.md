# BookTracker API - Complete API Reference

## Base Information

- **Base URL**: `http://localhost:8000/api/v1`
- **API Version**: 1.0.0
- **Content-Type**: `application/json`
- **Authentication**: None (future enhancement)

## Interactive Documentation

FastAPI provides auto-generated interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Book Endpoints

### List Books
```http
GET /api/v1/books/
```

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 100 | Maximum records to return |
| status | string | No | null | Filter by status: `want_to_read`, `reading`, `completed` |

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "total_pages": 464,
    "current_page": 120,
    "status": "reading",
    "date_added": "2024-09-15T10:30:00",
    "date_started": "2024-09-16T09:00:00",
    "date_finished": null,
    "rating": null,
    "notes": "Highly recommended"
  }
]
```

**Example Requests:**
```bash
# Get all books
curl http://localhost:8000/api/v1/books/

# Get only reading books
curl http://localhost:8000/api/v1/books/?status=reading

# Get first 10 books
curl http://localhost:8000/api/v1/books/?limit=10
```

---

### Get Single Book
```http
GET /api/v1/books/{book_id}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_id | integer | Yes | The book's unique ID |

**Response: 200 OK**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "total_pages": 464,
  "current_page": 120,
  "status": "reading",
  "date_added": "2024-09-15T10:30:00",
  "date_started": "2024-09-16T09:00:00",
  "date_finished": null,
  "rating": 5,
  "notes": "Highly recommended"
}
```

**Response: 404 Not Found**
```json
{
  "detail": "Book not found"
}
```

**Example Request:**
```bash
curl http://localhost:8000/api/v1/books/1
```

---

### Create Book
```http
POST /api/v1/books/
```

**Request Body:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| title | string | Yes | max 200 chars | Book title |
| author | string | Yes | max 200 chars | Author name |
| isbn | string | No | max 13 chars | ISBN number |
| total_pages | integer | Yes | > 0 | Total number of pages |
| current_page | integer | No | >= 0 | Current reading page (default: 0) |
| status | string | No | enum | `want_to_read`, `reading`, `completed` (default: want_to_read) |
| rating | integer | No | 1-5 | Book rating |
| notes | string | No | - | Additional notes |
| date_started | datetime | No | ISO 8601 | When book was started |
| date_finished | datetime | No | ISO 8601 | When book was finished |

**Request Example:**
```json
{
  "title": "The Pragmatic Programmer",
  "author": "David Thomas, Andrew Hunt",
  "isbn": "9780135957059",
  "total_pages": 352,
  "current_page": 0,
  "status": "want_to_read",
  "notes": "20th Anniversary Edition"
}
```

**Response: 201 Created**
```json
{
  "id": 2,
  "title": "The Pragmatic Programmer",
  "author": "David Thomas, Andrew Hunt",
  "isbn": "9780135957059",
  "total_pages": 352,
  "current_page": 0,
  "status": "want_to_read",
  "date_added": "2024-09-20T14:30:00",
  "date_started": null,
  "date_finished": null,
  "rating": null,
  "notes": "20th Anniversary Edition"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Pragmatic Programmer",
    "author": "David Thomas, Andrew Hunt",
    "total_pages": 352
  }'
```

---

### Update Book
```http
PUT /api/v1/books/{book_id}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_id | integer | Yes | The book's unique ID |

**Request Body:** (All fields optional - partial update supported)
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| title | string | max 200 chars | Book title |
| author | string | max 200 chars | Author name |
| isbn | string | max 13 chars | ISBN number |
| total_pages | integer | > 0 | Total number of pages |
| current_page | integer | >= 0 | Current reading page |
| status | string | enum | `want_to_read`, `reading`, `completed` |
| rating | integer | 1-5 | Book rating |
| notes | string | - | Additional notes |
| date_started | datetime | ISO 8601 | When book was started |
| date_finished | datetime | ISO 8601 | When book was finished |

**Request Example:**
```json
{
  "current_page": 150,
  "status": "reading",
  "date_started": "2024-09-21T10:00:00"
}
```

**Response: 200 OK**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "total_pages": 464,
  "current_page": 150,
  "status": "reading",
  "date_added": "2024-09-15T10:30:00",
  "date_started": "2024-09-21T10:00:00",
  "date_finished": null,
  "rating": null,
  "notes": "Highly recommended"
}
```

**Response: 404 Not Found**
```json
{
  "detail": "Book not found"
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/books/1 \
  -H "Content-Type: application/json" \
  -d '{"current_page": 150, "status": "reading"}'
```

---

### Delete Book
```http
DELETE /api/v1/books/{book_id}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_id | integer | Yes | The book's unique ID |

**Response: 200 OK**
Returns the deleted book object

**Response: 404 Not Found**
```json
{
  "detail": "Book not found"
}
```

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/books/1
```

---

## Reading Session Endpoints

### Create Reading Session
```http
POST /api/v1/books/{book_id}/sessions
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_id | integer | Yes | The book's unique ID |

**Request Body:**
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| start_time | datetime | Yes | ISO 8601 | Session start time |
| pages_read | integer | Yes | >= 0 | Number of pages read |
| notes | string | No | - | Session notes |

**Request Example:**
```json
{
  "start_time": "2024-09-21T14:30:00",
  "pages_read": 25,
  "notes": "Chapter 5 on functions"
}
```

**Response: 201 Created**
```json
{
  "id": 1,
  "book_id": 1,
  "start_time": "2024-09-21T14:30:00",
  "end_time": null,
  "pages_read": 25,
  "notes": "Chapter 5 on functions",
  "created_at": "2024-09-21T14:30:00",
  "duration_minutes": null,
  "is_active": true
}
```

**Side Effects:**
- Book's `current_page` is incremented by `pages_read`
- If book status is `want_to_read`, it changes to `reading`
- If `current_page >= total_pages`, status changes to `completed`
- Book's `date_started` is set if not already set

**Response: 404 Not Found**
```json
{
  "detail": "Book not found"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/books/1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2024-09-21T14:30:00",
    "pages_read": 25,
    "notes": "Great chapter"
  }'
```

---

### Get Sessions for Book
```http
GET /api/v1/books/{book_id}/sessions
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| book_id | integer | Yes | The book's unique ID |

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 100 | Maximum records to return |

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "book_id": 1,
    "start_time": "2024-09-21T14:30:00",
    "end_time": "2024-09-21T15:45:00",
    "pages_read": 25,
    "notes": "Chapter 5 on functions",
    "created_at": "2024-09-21T14:30:00",
    "duration_minutes": 75,
    "is_active": false
  }
]
```

**Example Request:**
```bash
curl http://localhost:8000/api/v1/books/1/sessions
```

---

### Get All Sessions
```http
GET /api/v1/sessions
```

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 100 | Maximum records to return |
| active_only | boolean | No | false | Return only active sessions |

**Response: 200 OK**
```json
[
  {
    "id": 1,
    "book_id": 1,
    "start_time": "2024-09-21T14:30:00",
    "end_time": "2024-09-21T15:45:00",
    "pages_read": 25,
    "notes": "Chapter 5 on functions",
    "created_at": "2024-09-21T14:30:00",
    "duration_minutes": 75,
    "is_active": false,
    "book": {
      "id": 1,
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "isbn": "9780132350884",
      "total_pages": 464,
      "current_page": 150,
      "status": "reading",
      "date_added": "2024-09-15T10:30:00",
      "date_started": "2024-09-21T10:00:00",
      "date_finished": null,
      "rating": 5,
      "notes": "Highly recommended"
    }
  }
]
```

**Example Requests:**
```bash
# Get all sessions
curl http://localhost:8000/api/v1/sessions

# Get only active sessions
curl http://localhost:8000/api/v1/sessions?active_only=true
```

---

### Get Single Session
```http
GET /api/v1/sessions/{session_id}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | integer | Yes | The session's unique ID |

**Response: 200 OK**
```json
{
  "id": 1,
  "book_id": 1,
  "start_time": "2024-09-21T14:30:00",
  "end_time": "2024-09-21T15:45:00",
  "pages_read": 25,
  "notes": "Chapter 5 on functions",
  "created_at": "2024-09-21T14:30:00",
  "duration_minutes": 75,
  "is_active": false,
  "book": {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    ...
  }
}
```

**Response: 404 Not Found**
```json
{
  "detail": "Reading session not found"
}
```

**Example Request:**
```bash
curl http://localhost:8000/api/v1/sessions/1
```

---

### End Reading Session
```http
PUT /api/v1/sessions/{session_id}/end
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | integer | Yes | The session's unique ID |

**Request Body:**
```json
{
  "end_time": "2024-09-21T15:45:00"
}
```

If `end_time` is not provided, current time is used.

**Response: 200 OK**
```json
{
  "id": 1,
  "book_id": 1,
  "start_time": "2024-09-21T14:30:00",
  "end_time": "2024-09-21T15:45:00",
  "pages_read": 25,
  "notes": "Chapter 5 on functions",
  "created_at": "2024-09-21T14:30:00",
  "duration_minutes": 75,
  "is_active": false
}
```

**Response: 404 Not Found**
```json
{
  "detail": "Reading session not found or already ended"
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/sessions/1/end \
  -H "Content-Type: application/json" \
  -d '{"end_time": "2024-09-21T15:45:00"}'
```

---

### Update Session
```http
PUT /api/v1/sessions/{session_id}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | integer | Yes | The session's unique ID |

**Request Body:** (All fields optional)
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| end_time | datetime | ISO 8601 | Session end time |
| pages_read | integer | >= 0 | Number of pages read |
| notes | string | - | Session notes |

**Request Example:**
```json
{
  "pages_read": 30,
  "notes": "Updated notes - covered more material"
}
```

**Response: 200 OK**
Returns updated session object

**Response: 404 Not Found**
```json
{
  "detail": "Reading session not found"
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/sessions/1 \
  -H "Content-Type: application/json" \
  -d '{"pages_read": 30}'
```

---

## Utility Endpoints

### Root
```http
GET /
```

**Response: 200 OK**
```json
{
  "message": "Welcome to Book Tracker API"
}
```

---

### Health Check
```http
GET /health
```

**Response: 200 OK**
```json
{
  "status": "healthy"
}
```

---

### Debug Info
```http
GET /debug
```

**Response: 200 OK (Connected)**
```json
{
  "database_tables": ["books", "reading_sessions"],
  "book_count": 5,
  "reading_session_count": 12,
  "models_loaded": ["Book", "ReadingSession"],
  "status": "connected"
}
```

**Response: 200 OK (Error)**
```json
{
  "error": "Database connection error message",
  "status": "error"
}
```

---

## Response Schemas

### Book Schema
```typescript
{
  id: number;
  title: string;              // max 200 chars
  author: string;             // max 200 chars
  isbn: string | null;        // max 13 chars
  total_pages: number;        // > 0
  current_page: number;       // >= 0
  status: "want_to_read" | "reading" | "completed";
  date_added: string;         // ISO 8601 datetime
  date_started: string | null;   // ISO 8601 datetime
  date_finished: string | null;  // ISO 8601 datetime
  rating: number | null;      // 1-5
  notes: string | null;
}
```

### Session Schema
```typescript
{
  id: number;
  book_id: number;
  start_time: string;         // ISO 8601 datetime
  end_time: string | null;    // ISO 8601 datetime
  pages_read: number;         // >= 0
  notes: string | null;
  created_at: string;         // ISO 8601 datetime
  duration_minutes: number | null;  // Computed field
  is_active: boolean;         // Computed field
}
```

### SessionWithBook Schema
```typescript
{
  // All Session fields plus:
  book: Book;                 // Full book object
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Book not found"
}
```

### 422 Unprocessable Entity (Validation Error)
```json
{
  "detail": [
    {
      "loc": ["body", "total_pages"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Datetime Format

All datetime fields use ISO 8601 format:
```
YYYY-MM-DDTHH:MM:SS
2024-09-21T14:30:00
```

Timezone-aware format (recommended):
```
YYYY-MM-DDTHH:MM:SS±HH:MM
2024-09-21T14:30:00-07:00
```

---

## Rate Limiting

Currently no rate limiting is implemented. Future enhancement.

---

## Pagination

List endpoints support pagination via `skip` and `limit` parameters:
- Default `skip`: 0
- Default `limit`: 100
- Maximum `limit`: 100

**Example:**
```bash
# Get records 11-20
curl "http://localhost:8000/api/v1/books/?skip=10&limit=10"
```

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

All methods and headers are allowed for these origins.

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create a book
book_data = {
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "total_pages": 464
}
response = requests.post(f"{BASE_URL}/books/", json=book_data)
book = response.json()
print(f"Created book ID: {book['id']}")

# Get all books
response = requests.get(f"{BASE_URL}/books/")
books = response.json()
print(f"Total books: {len(books)}")

# Log a reading session
session_data = {
    "start_time": "2024-09-21T14:30:00",
    "pages_read": 25,
    "notes": "Great chapter"
}
response = requests.post(f"{BASE_URL}/books/{book['id']}/sessions", json=session_data)
session = response.json()
print(f"Session duration: {session.get('duration_minutes')} minutes")
```

---

## JavaScript Client Example

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// Create a book
async function createBook() {
  const response = await fetch(`${BASE_URL}/books/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: 'Clean Code',
      author: 'Robert C. Martin',
      total_pages: 464
    })
  });
  const book = await response.json();
  console.log('Created book:', book);
  return book;
}

// Get all reading books
async function getReadingBooks() {
  const response = await fetch(`${BASE_URL}/books/?status=reading`);
  const books = await response.json();
  console.log('Currently reading:', books);
  return books;
}

// Update progress
async function updateProgress(bookId, currentPage) {
  const response = await fetch(`${BASE_URL}/books/${bookId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ current_page: currentPage })
  });
  return response.json();
}
```
