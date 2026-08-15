import sqlite3
from typing import Generator

DB_NAME = "cv_builder.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Users Table (Updated with Auth fields)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                phone TEXT,
                linkedin_url TEXT,
                github_url TEXT,
                portfolio_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Work Experiences Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT DEFAULT 'Present',
                description_bullets TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 3. Projects Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                technologies TEXT,
                description_bullets TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 4. Education Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS education (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                institution TEXT NOT NULL,
                degree TEXT NOT NULL,
                location TEXT,
                graduation_year TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 5. Certifications Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                issuing_organization TEXT NOT NULL,
                issue_date TEXT NOT NULL,
                expiration_date TEXT,
                credential_id_or_url TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        # 6. Skills Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                skills_list TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)

        conn.commit()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI Dependency for per-request database connection lifecycle."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()