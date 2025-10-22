# BookTracker - Development Guide

Developer documentation for contributing to BookTracker.

## Development Environment Setup

### Prerequisites
- Python 3.13+
- Docker Desktop
- Git
- Code editor (VS Code recommended)
- MySQL client (optional, for debugging)

### Initial Setup
```bash
# Clone the repository
git clone <repo-url>
cd rest_api_project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks (future)
# pre-commit install
```

### VS Code Setup (Recommended)
Install these extensions:
- Python
- Pylance
- SQLAlchemy ORM
- Docker
- REST Client

**settings.json**:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

## Project Architecture

### Backend Structure (FastAPI)
```
app/
├── api/endpoints/      # Route handlers (controllers)
├── core/              # Config, database, security
├── crud/              # Database operations (data layer)
├── models/            # SQLAlchemy ORM models
└── schemas/           # Pydantic validation schemas
```

### Design Patterns
- **Repository Pattern**: CRUD modules abstract database operations
- **Dependency Injection**: FastAPI's `Depends()` for DB sessions
- **Schema Validation**: Pydantic for request/response validation
- **ORM**: SQLAlchemy for database abstraction

### Data Flow
```
Request → Route Handler → CRUD Function → Database
                ↓
          Pydantic Schema (validation)
                ↓
        SQLAlchemy Model (ORM)
                ↓
          MySQL Database
```

## Code Style Guide

### Python (PEP 8)
```python
# Good
def create_book(db: Session, book: BookCreate) -> Book:
    """Create a new book in the database.

    Args:
        db: Database session
        book: Book data to create

    Returns:
        Created book instance
    """
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# Bad
def createBook(db,book):
    dbBook=Book(**book.dict())
    db.add(dbBook)
    db.commit()
    return dbBook
```

### Type Hints
Always use type hints:
```python
# Good
from typing import List, Optional

def get_books(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Book]:
    pass

# Bad
def get_books(db, skip=0, limit=100):
    pass
```

### Docstrings
Use Google-style docstrings:
```python
def calculate_reading_stats(book_id: int, db: Session) -> dict:
    """Calculate reading statistics for a book.

    Args:
        book_id: The book's unique identifier
        db: Database session for queries

    Returns:
        Dictionary containing:
            - total_sessions: Number of reading sessions
            - total_minutes: Total reading time
            - average_session: Average session duration
            - pages_per_hour: Reading speed metric

    Raises:
        HTTPException: If book not found (404)
    """
    pass
```

## Adding New Features

### Adding a New Book Field

**1. Update the SQLAlchemy Model** (`app/models/book.py`):
```python
class Book(Base):
    # ... existing fields ...
    publisher = Column(String(200), nullable=True)
    publication_year = Column(Integer, nullable=True)
```

**2. Update Pydantic Schemas** (`app/schemas/book.py`):
```python
class BookBase(BaseModel):
    # ... existing fields ...
    publisher: Optional[str] = Field(None, max_length=200)
    publication_year: Optional[int] = Field(None, ge=1000, le=9999)
```

**3. Run Migration** (when using Alembic):
```bash
alembic revision --autogenerate -m "Add publisher fields"
alembic upgrade head
```

Or for development (auto-create):
```python
# Tables will auto-create on app startup (main.py:20)
```

**4. Update CRUD if needed** (`app/crud/book.py`):
Usually no changes needed - SQLAlchemy handles it!

**5. Update Frontend** (`frontend/index.html`):
```javascript
// Update createBookCard function to display new fields
// Update addBookForm to include new inputs
```

### Adding a New Endpoint

**Example: Get Reading Statistics**

**1. Create Schema** (`app/schemas/book.py`):
```python
class ReadingStats(BaseModel):
    total_books: int
    books_reading: int
    books_completed: int
    total_pages_read: int
    average_rating: Optional[float]
    reading_streak_days: int
```

**2. Create CRUD Function** (`app/crud/book.py`):
```python
def get_reading_stats(db: Session) -> dict:
    """Calculate user's reading statistics."""
    total_books = db.query(Book).count()
    books_reading = db.query(Book).filter(
        Book.status == BookStatus.reading
    ).count()
    # ... more calculations ...

    return {
        "total_books": total_books,
        "books_reading": books_reading,
        # ... more stats ...
    }
```

**3. Create Route Handler** (`app/api/endpoints/books.py`):
```python
from app.schemas.book import ReadingStats

@router.get("/stats", response_model=ReadingStats)
def get_stats(db: Session = Depends(get_db)):
    """Get user's reading statistics."""
    stats = crud_book.get_reading_stats(db)
    return stats
```

**4. Test the Endpoint**:
```bash
curl http://localhost:8000/api/v1/books/stats
```

**5. Update Frontend** (if needed):
```javascript
async function fetchStats() {
    const response = await fetch(`${API_BASE_URL}/books/stats`);
    const stats = await response.json();
    displayStats(stats);
}
```

## Database Migrations

### Current Approach
Tables auto-create on startup via SQLAlchemy:
```python
# main.py
Base.metadata.create_all(bind=engine)
```

**Pros**: Simple, good for development
**Cons**: No version control, can't rollback

### Future: Alembic Migrations

**Setup**:
```bash
pip install alembic
alembic init alembic
```

**Generate Migration**:
```bash
alembic revision --autogenerate -m "Add publisher fields"
```

**Apply Migration**:
```bash
alembic upgrade head
```

**Rollback**:
```bash
alembic downgrade -1
```

## Testing

### Unit Tests (Future)
```python
# tests/test_crud_book.py
import pytest
from app.crud.book import create_book, get_book
from app.schemas.book import BookCreate

def test_create_book(db_session):
    """Test book creation."""
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        total_pages=200
    )

    book = create_book(db_session, book_data)

    assert book.id is not None
    assert book.title == "Test Book"
    assert book.current_page == 0
    assert book.status == BookStatus.want_to_read
```

### Integration Tests (Future)
```python
# tests/test_api_books.py
from fastapi.testclient import TestClient

def test_create_book_endpoint(client: TestClient):
    """Test POST /books/ endpoint."""
    response = client.post(
        "/api/v1/books/",
        json={
            "title": "Test Book",
            "author": "Test Author",
            "total_pages": 200
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert "id" in data
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_crud_book.py::test_create_book
```

## Debugging

### Debug Mode
FastAPI debug mode is controlled in `.env`:
```env
DEBUG=True
```

### Interactive Debugging
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use debugpy for VS Code
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()
```

### Database Debugging
```bash
# Connect to MySQL container
docker exec -it <container-name> mysql -uroot -p

# View tables
SHOW TABLES;

# View book data
SELECT * FROM books;

# View sessions
SELECT * FROM reading_sessions;
```

### API Request Debugging
```bash
# Verbose curl
curl -v http://localhost:8000/api/v1/books/

# Use httpie (better formatting)
pip install httpie
http GET localhost:8000/api/v1/books/
```

## Performance Optimization

### Database Queries

**Use indexes**:
```python
# models/book.py
class Book(Base):
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(BookStatus), index=True)  # Add index
```

**Eager loading for relationships**:
```python
from sqlalchemy.orm import joinedload

# Bad (N+1 queries)
sessions = db.query(ReadingSession).all()
for session in sessions:
    print(session.book.title)  # Each iteration queries DB

# Good (1 query)
sessions = db.query(ReadingSession).options(
    joinedload(ReadingSession.book)
).all()
```

**Pagination**:
```python
# Always use skip/limit for large datasets
def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Book).offset(skip).limit(limit).all()
```

### Response Optimization

**Use response_model_exclude_unset**:
```python
@router.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    # Only include fields that are actually set
    ...
```

### Caching (Future)
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_book_stats(book_id: int) -> dict:
    # Expensive calculation cached in memory
    pass
```

## Git Workflow

### Branching Strategy
```
main                 - Production-ready code
├── feature/frontend - Frontend features
├── feature/stats    - Statistics feature
└── fix/book-delete  - Bug fixes
```

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```bash
# Features
git commit -m "feat: add book statistics endpoint"

# Bug fixes
git commit -m "fix: correct pagination offset calculation"

# Documentation
git commit -m "docs: update API documentation"

# Refactoring
git commit -m "refactor: simplify CRUD book functions"

# Tests
git commit -m "test: add tests for reading sessions"
```

### Pull Request Process
1. Create feature branch from `main`
2. Make changes and commit
3. Push to remote
4. Create PR with description
5. Request review
6. Address feedback
7. Merge to main

## Environment Variables

### Development
```env
DATABASE_URL=mysql+pymysql://root:devpassword@localhost/booktracker_dev
DEBUG=True
APP_NAME=BookTracker API (Dev)
```

### Production
```env
DATABASE_URL=mysql+pymysql://user:prod_password@db-server/booktracker_prod
DEBUG=False
APP_NAME=BookTracker API
```

## Security Considerations

### SQL Injection Protection
SQLAlchemy ORM protects against SQL injection:
```python
# Safe - parameterized query
book = db.query(Book).filter(Book.id == book_id).first()

# Dangerous - string formatting (DON'T DO THIS)
# query = f"SELECT * FROM books WHERE id = {book_id}"
```

### Input Validation
Pydantic handles validation:
```python
class BookCreate(BaseModel):
    title: str = Field(..., max_length=200, min_length=1)
    total_pages: int = Field(..., gt=0, le=10000)
```

### CORS Configuration
Only allow trusted origins:
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Docker Configuration

### Build Custom Image (Future)
```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Future)
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: yourpassword
      MYSQL_DATABASE: booktracker_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: mysql+pymysql://root:yourpassword@db/booktracker_db

volumes:
  mysql_data:
```

## Useful Commands

```bash
# Database
docker exec -it <container> mysql -uroot -p
docker logs <container>
docker restart <container>

# Development
uvicorn main:app --reload --log-level debug
python -m app.core.database  # Test DB connection

# Dependencies
pip freeze > requirements.txt
pip install -r requirements.txt --upgrade

# Code Quality
pylint app/
black app/
mypy app/

# Git
git log --oneline --graph
git diff main...feature/branch
git rebase -i HEAD~3
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [MySQL 8.0 Reference](https://dev.mysql.com/doc/refman/8.0/en/)

## Getting Help

- Check existing issues in the repository
- Review API documentation at `/docs`
- Debug with `/debug` endpoint
- Use Python debugger (`pdb`) for step-through debugging
