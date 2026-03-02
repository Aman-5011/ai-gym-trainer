import sqlite3
import os
from gemini_service import PersonalizedFitnessAdvisor
from datetime import datetime

class DailyPlanSystem:
    def __init__(self,api_key=None, db_name="gym_trainer.db"):
        self.db_name = db_name
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        # Initialize AI Model
        self.advisor = PersonalizedFitnessAdvisor(api_key)
        self.init_table()

    def init_table(self):
        """Initializes the user_daily_plans table."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_daily_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                day_number INTEGER NOT NULL,
                plan_text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (username) REFERENCES users(username)
            );
        ''')
        conn.commit()
        conn.close()

    def generate_daily_plan(self, name, age, height, weight, fitness_level, goal, day_number):
        """Generates a structured daily workout and diet plan using AI."""
        prompt = f"""You are a professional fitness coach.

Create Day {day_number} structured plan for {name}.
User Profile: Age {age}, Height {height}cm, Weight {weight}kg, Level: {fitness_level}, Goal: {goal}.

Include:
1. Workout Focus
2. Exercise List (5-7 exercises)
3. Estimated Calories Burn
4. Diet Recommendation for Today
5. One Motivational Line

Keep between 150-220 words.
Clear formatting.
Friendly but professional tone."""

        try:
            return self.advisor.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            ).text
        except Exception as e:
            return f"Error generating daily plan: {str(e)}"

    def get_latest_day(self, username):
        """Returns the highest day_number for a user, or 0 if none exists."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MAX(day_number) FROM user_daily_plans 
            WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] is not None else 0

    def get_plan_for_day(self, username, day_number):
        """Returns plan details for a specific day or None."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT day_number, plan_text, completed 
            FROM user_daily_plans 
            WHERE username = ? AND day_number = ?
        ''', (username, day_number))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def create_new_day_plan(self, username, plan_text):
        """Creates a new plan entry in the database for the next consecutive day."""
        try:
            latest_day = self.get_latest_day(username)
            new_day_number = latest_day + 1
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_daily_plans (username, day_number, plan_text, created_at)
                VALUES (?, ?, ?, ?)
            ''', (username, new_day_number, plan_text, created_at))
            conn.commit()
            conn.close()
            return {"success": True, "day_number": new_day_number}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def mark_completed(self, username, day_number):
        """Marks a specific day's plan as completed in the database."""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_daily_plans 
                SET completed = 1 
                WHERE username = ? AND day_number = ?
            ''', (username, day_number))
            conn.commit()
            conn.close()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}