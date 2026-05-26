import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', 'senpay.db')

def get_db():
    """Retourne une connexion à la base SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise la base de données avec le schéma SQL."""
    conn = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("[DB] Base de données initialisée avec succès.")