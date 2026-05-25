import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open('app/models/schema.sql') as f:
        conn.executescript(f.read())
    conn.close()
