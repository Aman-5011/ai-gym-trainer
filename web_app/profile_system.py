import sqlite3
from datetime import datetime
from database import DatabaseManager

from validators import (
    validate_full_name,
    validate_age,
    validate_height,
    validate_weight,
    validate_goal,
    validate_fitness_level
)

class ProfileSystem:
    def __init__(self, db_name="gym_trainer.db"):
        self.db_name = db_name
        self.db_manager = DatabaseManager(db_name)

    def profile_exists(self, username):
        #Returns True if a profile exists for the given username, else False
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_profile WHERE username = ?", (username,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def create_profile(self, username, full_name, age, height, weight, goal, fitness_level):
        #Validates input fields and creates a new profile record with an initial timestamp
        try:
            validate_full_name(full_name)
            validate_age(age)
            validate_height(height)
            validate_weight(weight)
            validate_goal(goal)
            validate_fitness_level(fitness_level)

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_profile (
                    username, full_name, age, height, weight, goal, fitness_level, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, 
                full_name, 
                age, 
                height, 
                weight, 
                goal, 
                fitness_level,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()
            return {"success": True}

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Profile already exists for this user."}
        except Exception as e:
            return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

    def get_profile(self, username): #Fetches and returns the profile data for a specific username as a dictionary
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None
    
    def update_profile(self, username , full_name, age, height, weight, fitness_level, goal): #Updates biometrics and refreshes the updated_at timestamp.
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE user_profile
            SET full_name = ?, age = ?, height = ?, weight = ?, 
                fitness_level = ?, goal = ?, 
                updated_at = ?
            WHERE username = ?
        ''', (
            full_name,
            age,
            height,
            weight,
            fitness_level,
            goal,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username
        ))

        conn.commit()
        conn.close()