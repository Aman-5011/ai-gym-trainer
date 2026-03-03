from gemini_service import PersonalizedFitnessAdvisor
from database import DatabaseManager
from datetime import datetime

class DailyPlanSystem:
    def __init__(self, db_name="gym_trainer.db"):
        self.db_name = db_name
        self.db_manager = DatabaseManager(db_name)
        self.advisor = PersonalizedFitnessAdvisor()
        # self.init_table()

    # def init_table(self):
    #     """Initializes the user_daily_plans table."""
    #     conn = sqlite3.connect(self.db_name)
    #     cursor = conn.cursor()
    #     cursor.execute('''
    #         CREATE TABLE IF NOT EXISTS user_daily_plans (
    #             id INTEGER PRIMARY KEY AUTOINCREMENT,
    #             username TEXT NOT NULL,
    #             day_number INTEGER NOT NULL,
    #             plan_text TEXT NOT NULL,
    #             created_at TEXT NOT NULL,
    #             completed INTEGER DEFAULT 0,
    #             FOREIGN KEY (username) REFERENCES users(username)
    #         )
    #     ''')
    #     conn.commit()
    #     conn.close()

    def generate_daily_plan(self, name, age, height, weight, fitness_level, goal, day_number):
        """Calls the advisor specialist to get the AI text."""
        return self.advisor.generate_daily_plan_text(
            name, age, height, weight, fitness_level, goal, day_number
        )

    def get_latest_day(self, username): #Returns the highest day_number for a user, or 0 if none exists
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MAX(day_number) FROM user_daily_plans 
            WHERE username = ?
        ''', (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] is not None else 0

    def get_plan_for_day(self, username, day_number): 
        #Returns plan details for a specific day or None 
        #ye kuch generate nahi karega bas database se details laake dega
        #kyunki agar user same day dobara login karega to uske liya koyi naya plan nahi banaya jayega
        conn = self.db_manager.get_connection()
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
        #user agar naye din login karega to uske liye naya plan banayega ye
        try:
            latest_day = self.get_latest_day(username)
            new_day_number = latest_day + 1
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_daily_plans (username, day_number, plan_text, created_at)
                VALUES (?, ?, ?, ?)
            ''', (username, new_day_number, plan_text, created_at))
            conn.commit()
            conn.close()
            return {"success": True, "day_number": new_day_number} #ab ye dictionary return kar raha he 
        except Exception as e:
            return {"success": False, "error": str(e)}

    def mark_completed(self, username, day_number):
        try:
            conn = self.db_manager.get_connection()
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