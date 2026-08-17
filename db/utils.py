import sqlite3
from db.database import get_db
from typing import Optional, Dict, Any
from schema.models import UserRegisterSchema

def get_user_by_email(email:str)->Optional[Dict[str, Any]]:
    """Gets whole user record by email"""
    with get_db() as conn:
        row = conn.cursor().execute("SELECT id, full_name, email, hashed_password, phone, linkedin_url, github_url, portfolio_url FROM users WHERE email = ?",
        (email,)).fetchone()

        return dict(row) if row else None

def get_user_by_id(user_id:int)->Optional[Dict[str, Any]]:
    """Get whole user by id"""
    with get_db() as conn:
        row = conn.cursor().execute("SELECT id, full_name, email, phone, linkedin_url, github_url, portfolio_url FROM users WHERE id = ?",
        (user_id,)).fetchone()

        return dict(row) if row else None

def create_user(full_name:str, email:str, hashed_password:str)->int:
    """Insert new record into database"""

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (full_name, email, hashed_password) VALUES (?, ?, ?)",
        (full_name, email, hashed_password))
        conn.commit()


        return cursor.lastrowid()
