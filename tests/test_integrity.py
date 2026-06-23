import pytest
import sys
import os
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SENPAY_MASTER_KEY'] = 'unesuperclesecretede32characterss'

from app.audit.verifier import verify_tx_chain, compute_tx_hash
from datetime import datetime

def create_test_db():
    """Crée une base SQLite en mémoire avec la table transactions."""
    conn = sqlite3.connect(':memory:')
    conn.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            tx_type TEXT NOT NULL,
            tx_hash TEXT NOT NULL,
            prev_tx_hash TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def insert_tx(conn, sender_id, receiver_id, amount, tx_type, prev_tx_hash=''):
    """Insère une transaction avec son hash enchaîné."""
    ts = datetime.utcnow().isoformat() + 'Z'
    tx_hash = compute_tx_hash(sender_id, receiver_id, amount, tx_type, ts, prev_tx_hash)
    conn.execute(
        'INSERT INTO transactions(sender_id, receiver_id, amount, tx_type, tx_hash, prev_tx_hash, created_at)'
        ' VALUES(?, ?, ?, ?, ?, ?, ?)',
        (sender_id, receiver_id, amount, tx_type, tx_hash, prev_tx_hash, ts)
    )
    conn.commit()
    return tx_hash

def test_tx_hash_valid():
    """Chaîne de 5 transactions intègres est validée."""
    conn = create_test_db()
    prev = ''
    for i in range(5):
        prev = insert_tx(conn, sender_id=1, receiver_id=2, amount=5000, tx_type='transfer', prev_tx_hash=prev)
    ok, bad_id = verify_tx_chain(conn)
    assert ok == True
    assert bad_id is None

def test_tx_hash_tampered():
    """Modification du montant — détection immédiate."""
    conn = create_test_db()
    prev = ''
    for i in range(5):
        prev = insert_tx(conn, sender_id=1, receiver_id=2, amount=5000, tx_type='transfer', prev_tx_hash=prev)
    # Altérer le montant de la transaction id=3
    conn.execute("UPDATE transactions SET amount=999999 WHERE id=3")
    conn.commit()
    ok, bad_id = verify_tx_chain(conn)
    assert ok == False
    assert bad_id == 3