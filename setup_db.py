# import sqlite3

# DB_FILE = "compost_log.db"

# def initialize_db():
#     """Creates the SQLite database and compost_log table if they don't exist."""
#     conn = sqlite3.connect(DB_FILE)
#     c = conn.cursor()
    
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS compost_log (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             item TEXT,
#             weight REAL,
#             date TEXT
#         )
#     ''')
    
#     conn.commit()
#     conn.close()
#     print("✅ Database initialized successfully!")

# if __name__ == "__main__":
#     initialize_db()
