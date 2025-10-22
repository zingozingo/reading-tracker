# BookTracker API

A full-stack personal reading tracker application built with FastAPI, SQLAlchemy, and MySQL. Track your reading progress, log reading sessions, and manage your book collection with a modern dark-themed dashboard.

## Features

### Book Management
- **Full CRUD Operations** - Create, read, update, and delete books
- **Three Reading States** - Want to Read, Currently Reading, Completed
- **Progress Tracking** - Track current page and calculate reading progress
- **Book Metadata** - Title, author, ISBN, total pages, rating (1-5), and notes
- **Automatic Timestamping** - Track when books are added, started, and finished

### Reading Sessions
- **Session Logging** - Record start/end times for reading sessions
- **Page Progress** - Track pages read per session
- **Session Notes** - Add notes about each reading session
- **Duration Calculation** - Automatically calculate session duration
- **Active Session Tracking** - View all ongoing reading sessions
- **Auto Status Updates** - Books automatically move from "Want to Read" to "Reading" when first session is logged

### Dashboard UI
- **Dark Theme** - Modern, GitHub-style dark interface with forest green accents
- **Three-Column Layout** - Organized view of Currently Reading, Want to Read, and Completed books
- **Real-time Stats** - Total books, reading progress, completion counts
- **Interactive Progress Bars** - Click to update reading progress
- **Modal Forms** - Add books and log sessions with intuitive forms
- **Toast Notifications** - Visual feedback for all operations
- **Responsive Design** - Works on desktop and tablet screens

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **PyMySQL** - Pure Python MySQL driver
- **Uvicorn** - ASGI server for running FastAPI
- **Python 3.13** - Latest Python version

### Frontend
- **Vanilla JavaScript** - No frameworks, pure JS for maximum simplicity
- **HTML/CSS** - Modern CSS with CSS variables for theming
- **Simple HTTP Server** - Python-based static file server

### Database
- **MySQL 8.0** - Running in Docker container
- **Docker** - Containerized database for easy setup

## Project Structure

```
rest_api_project/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── books.py          # Book CRUD endpoints
│   │       └── sessions.py       # Reading session endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Pydantic settings management
│   │   └── database.py           # SQLAlchemy database setup
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── book.py               # Book database operations
│   │   └── reading_session.py   # Session database operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── book.py               # SQLAlchemy Book model
│   │   └── reading_session.py   # SQLAlchemy ReadingSession model
│   └── schemas/
│       ├── __init__.py
│       ├── book.py               # Pydantic Book schemas
│       └── reading_session.py   # Pydantic Session schemas
├── frontend/
│   ├── index.html                # Dashboard UI (1300+ lines)
│   └── serve.py                  # Frontend HTTP server
├── main.py                       # FastAPI application entry point
├── requirements.txt              # Python dependencies
├── .env                          # Environment configuration
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Database Schema

### Books Table
```sql
CREATE TABLE books (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200) NOT NULL,
    isbn VARCHAR(13),
    total_pages INT NOT NULL,
    current_page INT DEFAULT 0,
    status ENUM('want_to_read', 'reading', 'completed') DEFAULT 'want_to_read',
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_started DATETIME,
    date_finished DATETIME,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    notes TEXT
);
```

### Reading Sessions Table
```sql
CREATE TABLE reading_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    pages_read INT NOT NULL DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
```

## Setup Instructions

### Prerequisites
- Python 3.13+
- Docker (for MySQL)
- Git

### 1. Clone the Repository
```bash
cd ~/Desktop/all_py_scripts
git clone <repository-url> rest_api_project
cd rest_api_project
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database
If you don't have a MySQL container running, start one:
```bash
docker run -d \
  --name booktracker-mysql \
  -e MYSQL_ROOT_PASSWORD=yourpassword \
  -e MYSQL_DATABASE=booktracker_db \
  -p 3306:3306 \
  mysql:8.0
```

Or use an existing MySQL instance and create the database:
```bash
docker exec -it <mysql-container> mysql -uroot -p
CREATE DATABASE booktracker_db;
```

### 5. Configure Environment
Create or update `.env` file:
```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost/booktracker_db

# Application Configuration
APP_NAME=BookTracker API
APP_VERSION=1.0.0
DEBUG=True

# Server Configuration
PORT=8000

# API Configuration
API_V1_STR=/api/v1
```

## Running the Application

### Start Backend API
```bash
# Terminal 1
source venv/bin/activate
uvicorn main:app --reload
```
The API will be available at http://localhost:8000

### Start Frontend Dashboard
```bash
# Terminal 2
python frontend/serve.py
```
The dashboard will be available at http://localhost:3000

### Verify Everything Works
```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/debug

# View API documentation
open http://localhost:8000/docs
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Book Endpoints

#### List All Books
```http
GET /books/?skip=0&limit=100&status=reading
```
Query Parameters:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)
- `status` (optional): Filter by status (want_to_read, reading, completed)

#### Get Single Book
```http
GET /books/{book_id}
```

#### Create Book
```http
POST /books/
Content-Type: application/json

{
  "title": "The Pragmatic Programmer",
  "author": "David Thomas, Andrew Hunt",
  "isbn": "9780135957059",
  "total_pages": 352,
  "current_page": 0,
  "status": "want_to_read",
  "rating": null,
  "notes": "Recommended by colleague"
}
```

#### Update Book
```http
PUT /books/{book_id}
Content-Type: application/json

{
  "current_page": 125,
  "status": "reading",
  "date_started": "2024-09-15T10:00:00"
}
```

#### Delete Book
```http
DELETE /books/{book_id}
```

### Reading Session Endpoints

#### Create Reading Session
```http
POST /books/{book_id}/sessions
Content-Type: application/json

{
  "start_time": "2024-09-20T14:30:00",
  "pages_read": 25,
  "notes": "Great chapter on refactoring"
}
```
Note: Creating a session automatically updates book progress

#### Get Sessions for a Book
```http
GET /books/{book_id}/sessions?skip=0&limit=100
```

#### Get All Sessions
```http
GET /sessions?skip=0&limit=100&active_only=false
```

#### Get Single Session
```http
GET /sessions/{session_id}
```

#### End Reading Session
```http
PUT /sessions/{session_id}/end
Content-Type: application/json

{
  "end_time": "2024-09-20T15:45:00"
}
```

#### Update Session
```http
PUT /sessions/{session_id}
Content-Type: application/json

{
  "pages_read": 30,
  "notes": "Updated notes"
}
```

### Utility Endpoints

#### Root
```http
GET /
```
Returns welcome message

#### Health Check
```http
GET /health
```
Returns service health status

#### Debug Info
```http
GET /debug
```
Returns database connection status, table names, and record counts

## Frontend Features

### Dashboard Interface
Access at http://localhost:3000

#### Stats Cards (Top Bar)
- Total Books count
- Currently Reading count with average progress
- Completed Books count
- Want to Read count

#### Three-Column Grid
1. **Currently Reading** - Books in progress
2. **Want to Read** - Books in queue
3. **Completed** - Finished books

#### Book Cards
Each book card displays:
- Title and author
- Status badge
- Current page / Total pages
- Progress bar (clickable to update progress)
- Rating stars (if rated)
- Action buttons:
  - Want to Read: "START" button
  - Reading: "LOG" button (log reading session)
  - Completed: "REREAD" button
- Page input for manual updates
- Delete button

#### Add Book Modal
Click the "+" floating action button to add a new book:
- Title (required)
- Author (required)
- ISBN (optional)
- Total Pages (required, min: 10)
- Current Page (optional)
- Status (dropdown)

#### Log Reading Session Modal
Click "LOG" on a reading book to record a session:
- Start Time (datetime picker)
- End Time (datetime picker)
- Duration (auto-calculated)
- Pages Read (number input)
- Notes (optional textarea)

### Keyboard Shortcuts
- Press "R" to refresh data (when focused on dashboard)

### Auto-Refresh
Dashboard automatically refreshes data every 30 seconds

## Development Workflow

### Running Tests
```bash
# Add tests here when implemented
pytest
```

### Code Style
The project follows:
- PEP 8 for Python code
- Type hints for function signatures
- Pydantic models for validation
- SQLAlchemy ORM for database operations

### Database Migrations
Currently using SQLAlchemy's `create_all()` for table creation. For production, consider using Alembic:
```bash
# Future implementation
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Git Workflow
Current branches:
- `main` - Production-ready code
- `feature/frontend` - Frontend development (currently active)

```bash
# Create a new feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Add your feature"

# Push to remote
git push origin feature/your-feature-name
```

## Troubleshooting

### Database Connection Issues

**Error: Access denied for user 'root'@'localhost'**
- Check your `.env` file has the correct password
- Verify MySQL container is running: `docker ps`
- Test connection: `docker exec -it <container> mysql -uroot -p`

**Error: Port 3306 already in use**
- Check what's using the port: `lsof -ti:3306`
- Use the existing MySQL container or stop the conflicting service

### API Not Starting

**Error: Port 8000 already in use**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --reload --port 8001
```

### Frontend Not Loading

**Error: Port 3000 already in use**
```bash
# Find and kill the process
lsof -ti:3000 | xargs kill -9

# Or modify frontend/serve.py to use a different port
```

**Dashboard shows "Connection Error"**
- Verify backend API is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors
- Ensure CORS settings in main.py:11-17 include your frontend URL

### Database Tables Not Created

**Error: Table doesn't exist**
```bash
# Tables should auto-create, but if they don't:
# Check main.py:20-24 for table creation
# Verify database exists
docker exec -it <container> mysql -uroot -p -e "SHOW DATABASES;"
```

## API Response Examples

### Successful Book Creation
```json
{
  "id": 1,
  "title": "The Pragmatic Programmer",
  "author": "David Thomas, Andrew Hunt",
  "isbn": "9780135957059",
  "total_pages": 352,
  "current_page": 0,
  "status": "want_to_read",
  "date_added": "2024-09-15T10:30:00",
  "date_started": null,
  "date_finished": null,
  "rating": null,
  "notes": "Recommended by colleague"
}
```

### Reading Session with Computed Fields
```json
{
  "id": 1,
  "book_id": 1,
  "start_time": "2024-09-20T14:30:00",
  "end_time": "2024-09-20T15:45:00",
  "pages_read": 25,
  "notes": "Great chapter on refactoring",
  "created_at": "2024-09-20T14:30:00",
  "duration_minutes": 75,
  "is_active": false
}
```

### Error Response
```json
{
  "detail": "Book not found"
}
```

## Computed Fields

### Reading Sessions
- `duration_minutes` - Calculated from start_time and end_time
- `is_active` - Boolean indicating if session is ongoing (no end_time)

## Business Logic

### Automatic Status Updates
1. **Starting a Book**: When first reading session is created, book status changes from `want_to_read` to `reading`
2. **Completing a Book**: When `current_page >= total_pages`, status changes to `completed`
3. **Re-reading**: Completed books can be moved back to `reading` with progress reset to page 0

### Progress Calculation
```python
progress = (current_page / total_pages) * 100
```
Capped at 100% maximum

## Future Enhancements

Potential features to add:
- [ ] User authentication and authorization
- [ ] Book recommendations based on reading history
- [ ] Reading goals and challenges
- [ ] Export data to CSV/JSON
- [ ] Book covers from Open Library API
- [ ] Reading statistics and charts
- [ ] Mobile app version
- [ ] Social features (share progress, reviews)
- [ ] Integration with Goodreads
- [ ] Reading streak tracking

## License

Private project - All rights reserved

## Contact

For issues or questions, contact the development team.

---

Built with ❤️ using FastAPI and modern web technologies
