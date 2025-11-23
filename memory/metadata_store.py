import sqlite3
from datetime import datetime


class MetadataStore:
    def __init__(self, db_path="metadata.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init()

    def init(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            idx INTEGER PRIMARY KEY,
            text TEXT,
            tag TEXT,
            date TEXT
        );
        """)

    def add(self, idx, text, tag):
        date = datetime.utcnow().isoformat()
        self.conn.execute(
            "INSERT INTO messages (idx, text, tag, date) VALUES (?, ?, ?, ?)",
            (idx, text, tag, date)
        )
        self.conn.commit()

    def get(self, idx):
        cur = self.conn.execute(
            "SELECT text, tag, date FROM messages WHERE idx = ?",
            (idx,)
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "text": row[0],
            "tag": row[1],
            "date": row[2]
        }
