import sqlite3
import hashlib
import os
from datetime import datetime
from database import DatabaseManager  # Centralized schema manager
from validators import (
    validate_username,
    validate_password,
    validate_profile_data,
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

    def save_profile(self, username, age, height, weight, fitness_level, goal):  #Saves or updates user profile data
        try:
            validate_profile_data(age, height, weight)
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                INSERT INTO user_profile (username, age, height, weight, fitness_level, goal, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    age=excluded.age,
                    height=excluded.height,
                    weight=excluded.weight,
                    fitness_level=excluded.fitness_level,
                    goal=excluded.goal,
                    updated_at=excluded.updated_at
            ''', (username, age, height, weight, fitness_level, goal, updated_at))
            
            conn.commit()
            conn.close()
            return {"success": True}
        except ValueError as ve:
            return {"success": False, "error": str(ve)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_profile(self, username): #Returns profile dictionary with calculated BMI
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_profile WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            profile = dict(row)
            if profile.get('height') and profile.get('weight'):
                height_m = profile['height'] / 100
                profile['bmi'] = round(profile['weight'] / (height_m ** 2), 2)
            return profile
        return None

    def save_workout(self, username, exercise, reps, accuracy, calories_burned, target_completed): #Logs a completed workout session
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO workout_history (username, date, exercise, reps, accuracy, calories_burned, target_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, date_str , exercise, reps, accuracy, calories_burned, target_completed))
        
        conn.commit()
        conn.close()

    def get_latest_workout(self, username): #Fetches the most recent workout session
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM workout_history
            WHERE username = ? 
            ORDER BY date DESC 
            LIMIT 1
        ''', (username,))

        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_workouts(self, username): #Fetches the full workout history
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT exercise, reps, accuracy, calories_burned, target_completed, date
            FROM workout_history
            WHERE username = ?
            ORDER BY date DESC
        ''', (username,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_user_progress(self, username): #Returns aggregated progress stats
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                COUNT(id), 
                SUM(reps), 
                AVG(accuracy), 
                SUM(calories_burned),
                MAX(date)
            FROM workout_history 
            WHERE username = ?
        ''', (username,))
        
        stats = cursor.fetchone()
        conn.close()

        return {
            "total_workouts": stats[0] or 0,
            "total_reps": stats[1] or 0,
            "average_accuracy": round(stats[2], 2) if stats[2] else 0,
            "total_calories": round(stats[3], 2) if stats[3] else 0,
            "last_workout_date": stats[4] or "No records"
        }