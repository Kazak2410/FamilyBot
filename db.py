import sqlite3


class DataBase:
    def __init__(self, filename):
        self.connection = sqlite3.connect(f"{filename}.db")
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                photo TEXT
            )
        """)

    def registrate_user(self, name, photo):
        self.cursor.execute("""
            INSERT OR IGNORE INTO users (name, photo) VALUES (?, ?)
        """, (name, photo))
        self.connection.commit()

    def get_users(self):
        self.cursor.execute("""
            SELECT name FROM users
        """)
        return " ".join(name[0] for name in self.cursor.fetchall())

    def check_table(self):
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type='table' AND name='users')")
        exists = self.cursor.fetchone()[0]
        return exists
