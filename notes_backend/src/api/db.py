import sqlite3
from contextlib import contextmanager
from typing import Optional

# Database file path - using the existing database
DATABASE_PATH = "/home/kavia/workspace/code-generation/simple-notes-app-311941-311980/database/myapp.db"


@contextmanager
def get_db_connection():
    """
    PUBLIC_INTERFACE
    Context manager for database connections.
    
    Yields:
        sqlite3.Connection: Database connection with row factory enabled
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def dict_from_row(row: sqlite3.Row) -> dict:
    """
    PUBLIC_INTERFACE
    Convert sqlite3.Row to dictionary.
    
    Args:
        row: SQLite row object
        
    Returns:
        dict: Dictionary representation of the row
    """
    return {key: row[key] for key in row.keys()}
