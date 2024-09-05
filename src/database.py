import sqlite3
import json
from typing import Dict, List

class Database:
    def __init__(self, db_name: str = "usermanpro.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
        self.add_created_at_column()
        self.update_created_at_column()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assistants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                chat_history TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_created_at_column(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            ALTER TABLE assistants ADD COLUMN created_at TIMESTAMP
        ''')
        self.conn.commit()

    def update_created_at_column(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE assistants SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL
        ''')
        self.conn.commit()

    def add_assistant(self, name: str, prompt: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO assistants (name, prompt, chat_history) VALUES (?, ?, ?)",
            (name, prompt, json.dumps([]))
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all_assistants(self) -> Dict[int, Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, prompt, chat_history FROM assistants")
        assistants = {}
        for row in cursor.fetchall():
            assistants[row[0]] = {
                "name": row[1],
                "prompt": row[2],
                "chat_history": json.loads(row[3])
            }
        return assistants

    def update_chat_history(self, assistant_id: int, chat_history: List[Dict]):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE assistants SET chat_history = ? WHERE id = ?",
            (json.dumps(chat_history), assistant_id)
        )
        self.conn.commit()

    def delete_assistant(self, assistant_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM assistants WHERE id = ?", (assistant_id,))
        self.conn.commit()
    
    def get_assistants_created_per_day(self) -> Dict[str, int]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DATE(created_at) AS date, COUNT(*) AS count
            FROM assistants
            GROUP BY date
        ''')
        data = {}
        for row in cursor.fetchall():
            data[row[0]] = row[1]
        return data
