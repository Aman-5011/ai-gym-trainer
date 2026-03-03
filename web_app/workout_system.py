from datetime import datetime
from database import DatabaseManager

class WorkoutSystem:
    def __init__(self, db_name="gym_trainer.db"):
        self.db_name=db_name
        self.db_manager = DatabaseManager(db_name)

    def save_workout(self, username, exercise, reps, accuracy, calories_burned, target_completed):
        #jese hi workout complete karoge.to ye voh data workout history me daalega
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO workout_history (username, date, exercise, reps, accuracy, calories_burned, target_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, date_str , exercise, reps, accuracy, calories_burned, target_completed))
        
        conn.commit()
        conn.close()

    def get_latest_workout(self, username):
        #hamne dashboard par recentaly konsi exercise karri h uska data dala he voh kaam ye karega 
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

    def get_all_workouts(self, username):
        #progress me sara data show kiya he to voh ye karega 
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
