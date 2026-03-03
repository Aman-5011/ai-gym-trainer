import sqlite3
import hashlib
from datetime import datetime
from database import DatabaseManager  # Centralized schema manager
from validators import (
    validate_username,
    validate_password,
)

class AuthSystem:
    def __init__(self, db_name="gym_trainer.db"):
        self.db_name = db_name
        self.db_manager = DatabaseManager(db_name)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password):
        #Creates a new user using structured dictionary returns
        try:
            validate_username(username)
            validate_password(password)
        except ValueError as ve:
            return {"success": False, "error": str(ve)}

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        try:
            # Check for existing username
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return {"success": False, "error": "Username already exists."}

            password_hash = self._hash_password(password)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                INSERT INTO users (username, password_hash, created_at)
                VALUES (?, ?, ?)
            ''', (username, password_hash, created_at))
            
            conn.commit()
            return {"success": True, "user_id": username}

        except sqlite3.Error as e:
            return {"success": False, "error": f"Database Error: {e}"}
        finally:
            conn.close()

    def login_user(self, username, password): #Verifies credentials and returns username if valid
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        password_hash = self._hash_password(password)

        cursor.execute('''
            SELECT username FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
