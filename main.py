from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.models import Book, ReadingSession  # Import the models to register them
from app.api.endpoints import books, sessions

app = FastAPI(title=settings.project_name)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create database tables. Error: {e}")
    print("The API will still work, but database operations may fail.")
    print("Please ensure MySQL is running and the database 'booktracker_db' exists.")

app.include_router(books.router, prefix=settings.api_v1_str + "/books", tags=["books"])
app.include_router(sessions.router, prefix=settings.api_v1_str, tags=["reading-sessions"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Book Tracker API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/debug")
def debug_info():
    from app.core.database import SessionLocal
    from sqlalchemy import inspect

    db = SessionLocal()
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Try to query books
        book_count = db.query(Book).count()
        session_count = db.query(ReadingSession).count()

        return {
            "database_tables": tables,
            "book_count": book_count,
            "reading_session_count": session_count,
            "models_loaded": ["Book", "ReadingSession"],
            "status": "connected"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
    finally:
        db.close()