from datetime import datetime
from database import DatabaseManager

class ChatSystem:
    def __init__(self, db_name="gym_trainer.db"):
        self.db_manager = DatabaseManager(db_name)

    def save_message(self, username, message, sender):
        """Saves a message to the chat_history table."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO chat_history (username, message, sender, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (username, message, sender, timestamp))
        
        conn.commit()
        conn.close()

    def get_history(self, username):
        """Retrieves history and converts rows to dictionaries for JSON compatibility."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT message, sender FROM chat_history WHERE username = ? ORDER BY id ASC', (username,))
        rows = cursor.fetchall()
        conn.close()
        
        # This conversion is required to avoid JSON errors
        return [dict(row) for row in rows]

    def clear_history(self, username):
        """Deletes all messages for a specific user."""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE username = ?", (username,))
        conn.commit()
        conn.close()