import sqlite3


class DataBase:
    def __init__(self, filename):
        self.connection = sqlite3.connect(f"{filename}.db")
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

    def insert_user(self, user):
        self.cursor.execute("""
            INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)
        """, (user.from_user.id, user.from_user.first_name))
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
