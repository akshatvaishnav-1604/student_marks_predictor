"""
database.py - Database Layer for Student Marks Manager.

This module handles SQLite database connectivity, schema creation,
and table initialization using Python's built-in sqlite3 library.
"""

from contextlib import contextmanager
import sqlite3
from typing import Generator

# Default database filename
DEFAULT_DB_NAME = "student_records.db"


@contextmanager
def get_db_connection(db_name: str = DEFAULT_DB_NAME) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields an active SQLite connection and guarantees
    proper closing of the connection upon exiting the context.

    Configures sqlite3.Row as the row_factory so query results can be
    accessed like dictionaries (by column name) as well as tuples (by index).

    Args:
        db_name (str): Path or name of the SQLite database file.

    Yields:
        sqlite3.Connection: Active database connection object.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_connection(db_name: str = DEFAULT_DB_NAME) -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database.

    Args:
        db_name (str): Path or name of the SQLite database file.

    Returns:
        sqlite3.Connection: Active database connection object.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_name: str = DEFAULT_DB_NAME) -> None:
    """
    Initializes the database by creating the `students` table if it doesn't already exist.

    Table Schema:
        - roll_no: INTEGER PRIMARY KEY (Unique identifier for each student)
        - name: TEXT NOT NULL (Student full name)
        - physics: REAL CHECK(physics BETWEEN 0 AND 100)
        - chemistry: REAL CHECK(chemistry BETWEEN 0 AND 100)
        - maths: REAL CHECK(maths BETWEEN 0 AND 100)
        - total: REAL (Sum of physics + chemistry + maths)
        - percentage: REAL ((total / 300) * 100)
        - grade: TEXT (Letter grade: A+, A, B, C, D, F)

    Args:
        db_name (str): Database file path to initialize.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS students (
        roll_no INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        physics REAL CHECK(physics BETWEEN 0 AND 100),
        chemistry REAL CHECK(chemistry BETWEEN 0 AND 100),
        maths REAL CHECK(maths BETWEEN 0 AND 100),
        total REAL,
        percentage REAL,
        grade TEXT
    );
    """
    with get_db_connection(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
