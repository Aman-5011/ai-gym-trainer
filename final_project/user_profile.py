import sqlite3
import os

class UserProfileManager:
    """
    Handles user profile creation, validation, and persistent storage using SQLite.
    Provides methods to retrieve profiles and log workout sessions.
    """

    def __init__(self, db_name="fitness_app.db"):
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        """Creates the necessary tables if they do not exist."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Table for storing user personal information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                fitness_level TEXT,
                goal TEXT
            )
        ''')
        
        # Table for logging historical workout data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                exercise TEXT,
                reps INTEGER,
                accuracy REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_new_profile(self):
        """
        Prompts user for input via text, validates data, and saves to database.
        Returns the unique user ID created.
        """
        print("\n--- User Profile Setup ---")
        name = input("Enter Name (Optional): ").strip() or "Guest"
        
        try:
            age = int(input("Enter Age: "))
            height = float(input("Enter Height (cm): "))
            weight = float(input("Enter Weight (kg): "))
        except ValueError:
            print("Invalid numerical input. Profile creation failed.")
            return None

        level = input("Fitness Level (beginner/intermediate/advanced): ").lower().strip()
        if level not in ['beginner', 'intermediate', 'advanced']:
            level = 'beginner'

        goal = input("Primary Goal (fat loss/muscle gain/endurance/general fitness): ").lower().strip()

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, age, height, weight, fitness_level, goal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, age, height, weight, level, goal))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        print(f"Profile saved successfully! User ID: {user_id}")
        return user_id

    def get_user_profile(self, user_id):
        """
        Retrieves user data for a specific ID.
        Returns a dictionary of profile data or None if not found.
        """
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def save_workout_session(self, user_id, exercise, reps, accuracy):
        """
        Logs a completed workout session to the database.
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO workout_logs (user_id, exercise, reps, accuracy)
            VALUES (?, ?, ?, ?)
        ''', (user_id, exercise, reps, accuracy))
        conn.commit()
        conn.close()
        return True

# Helper functions for external modules
def setup_user():
    manager = UserProfileManager()
    return manager.create_new_profile()

def get_user_profile(user_id):
    manager = UserProfileManager()
    return manager.get_user_profile(user_id)

def save_workout_session(user_id, exercise, reps, accuracy):
    manager = UserProfileManager()
    return manager.save_workout_session(user_id, exercise, reps, accuracy)

if __name__ == "__main__":
    # Internal test logic
    uid = setup_user()
    if uid:
        print(get_user_profile(uid))
        save_workout_session(uid, "Squats", 15, 85.5)