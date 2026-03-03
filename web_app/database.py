import sqlite3

class DatabaseManager:
    def __init__(self, db_name="gym_trainer.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row 
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        # 2. User Profile Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                username TEXT PRIMARY KEY,
                full_name TEXT,
                age INTEGER,
                height REAL,
                weight REAL,
                goal TEXT,
                fitness_level TEXT,
                updated_at TEXT,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        # 3. Workout History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                date TEXT,
                exercise TEXT,
                reps INTEGER,
                accuracy REAL,
                calories_burned REAL,
                target_completed INTEGER,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
        # 4. User Daily Plan Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_daily_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                day_number INTEGER NOT NULL,
                plan_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        conn.commit()
        conn.close()