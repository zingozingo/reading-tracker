# BookTracker - Quick Start Guide

Get BookTracker up and running in 5 minutes!

## Prerequisites

- Python 3.13+ installed
- Docker installed and running
- Terminal/Command Line access

## Step-by-Step Setup

### 1. Navigate to Project
```bash
cd ~/Desktop/all_py_scripts/rest_api_project
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```
You should see `(venv)` in your terminal prompt.

### 3. Check MySQL Container
```bash
# List all MySQL containers
docker ps -a | grep mysql
```

You should see a MySQL container running. If not, start one:
```bash
docker run -d \
  --name booktracker-mysql \
  -e MYSQL_ROOT_PASSWORD=yourpassword \
  -e MYSQL_DATABASE=booktracker_db \
  -p 3306:3306 \
  mysql:8.0
```

### 4. Verify Environment Configuration
Check that your `.env` file matches your MySQL setup:
```bash
cat .env
```

Should contain:
```
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost/booktracker_db
```

If the password doesn't match, update `.env` with the correct password.

### 5. Start Backend Server
```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Keep this terminal running and open a new terminal for the next step.

### 6. Start Frontend Server
In a new terminal:
```bash
cd ~/Desktop/all_py_scripts/rest_api_project
python frontend/serve.py
```

You should see:
```
============================================================
🚀 BookTracker Frontend Server
============================================================

📁 Serving directory: /Users/.../frontend
🌐 Server starting on port 3000...

✅ Server running successfully!
```

### 7. Access the Dashboard
Open your browser and navigate to:
```
http://localhost:3000
```

You should see the BookTracker dashboard with a dark theme!

### 8. Test the API (Optional)
In a new terminal:
```bash
# Check health
curl http://localhost:8000/health

# Check database
curl http://localhost:8000/debug

# View API docs
open http://localhost:8000/docs
```

## Using BookTracker

### Add Your First Book
1. Click the **+** button (bottom right)
2. Fill in the form:
   - Title: "Clean Code"
   - Author: "Robert C. Martin"
   - Total Pages: 464
   - Status: "Want to Read"
3. Click **ADD BOOK**

The book appears in the "Want to Read" column!

### Start Reading
1. Click **START** on the book card
2. The book moves to "Currently Reading"

### Log a Reading Session
1. Click **LOG** on a reading book
2. Fill in the session details:
   - Start Time: (auto-filled to now)
   - End Time: (select when you finished)
   - Pages Read: 25
   - Notes: "Great chapter on functions"
3. Click **SAVE SESSION**

Your progress updates automatically!

### Update Progress Manually
1. Click on the progress bar to set progress visually
2. Or type in the page input box and press Enter

### Complete a Book
When you update your current page to match total pages, the book automatically moves to "Completed"!

## Stopping the Servers

### Stop Frontend Server
In the frontend terminal, press:
```
Ctrl + C
```

### Stop Backend Server
In the backend terminal, press:
```
Ctrl + C
```

### Stop MySQL (if needed)
```bash
docker stop booktracker-mysql
```

## Common Issues

### "Connection Error" in Dashboard
**Problem**: Dashboard can't connect to API

**Solution**:
1. Check backend is running: `curl http://localhost:8000/health`
2. If not running, restart: `uvicorn main:app --reload`

### Database Connection Failed
**Problem**: API shows database error in `/debug`

**Solution**:
1. Check MySQL is running: `docker ps | grep mysql`
2. Check password in `.env` matches MySQL container
3. Restart backend server after updating `.env`

### Port Already in Use
**Problem**: Error starting server - port in use

**Solution**:
```bash
# For port 8000
lsof -ti:8000 | xargs kill -9

# For port 3000
lsof -ti:3000 | xargs kill -9
```

## Next Steps

- Read the full [README.md](../README.md) for detailed features
- Explore the [API Documentation](API.md) for integration
- Check the [Database Schema](../README.md#database-schema)

## Quick Reference

| Resource | URL |
|----------|-----|
| Dashboard | http://localhost:3000 |
| API Docs | http://localhost:8000/docs |
| API Base | http://localhost:8000/api/v1 |
| Health Check | http://localhost:8000/health |

**Happy Reading!** 📚
