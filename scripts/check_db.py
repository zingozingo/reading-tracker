#!/usr/bin/env python3
"""Database health check script for Makefile"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    try:
        from app.core.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text('SELECT 1')).fetchone()
            print('  \033[0;32m✓ Database connection successful\033[0m')

            # Get database name
            result = conn.execute(text('SELECT DATABASE()')).fetchone()
            print(f'  \033[0;32m✓ Connected to database: {result[0]}\033[0m')

        return 0

    except ImportError as e:
        print(f'  \033[0;31m✗ Import error: {e}\033[0m')
        print('  \033[0;33mRun: make install\033[0m')
        return 1

    except Exception as e:
        print('  \033[0;31m✗ Database connection failed!\033[0m')
        print(f'  \033[0;31mError: {e}\033[0m')
        print('')
        print('  \033[0;33mPossible solutions:\033[0m')
        print('  1. Check if MySQL is running: brew services list')
        print('  2. Start MySQL: brew services start mysql')
        print('  3. Check .env file for correct DATABASE_URL')
        print('  4. Verify MySQL port 3306 is accessible: lsof -i:3306')
        return 1

if __name__ == '__main__':
    sys.exit(main())
