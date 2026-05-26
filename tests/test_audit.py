import pytest
import sys
import os
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SENPAY_MASTER_KEY'] = 'unesuperclesecretede32characterss'

from app.audit.logger import log_action, compute_hmac
from app.audit.verifier import verify_audit_chain

def create_test_db():
    """Crée une base SQLite en mémoire avec la table audit_log."""
    conn = sqlite3.connect(':memory:')
    conn.execute('''
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            detail TEXT,
            amount REAL,
            timestamp TEXT NOT NULL,
            hmac TEXT NOT NULL,
            prev_hmac TEXT
        )
    ''')
    conn.commit()
    return conn

def test_hmac_chain_valid():
    """Une chaîne de 10 entrées intègres est validée."""
    conn = create_test_db()
    for i in range(10):
        log_action(conn, user_id=i, action='LOGIN', detail='test', amount=0)
    ok, bad_id = verify_audit_chain(conn)
    assert ok == True
    assert bad_id is None

def test_hmac_chain_tampered():
    """Altération d'une entrée — la vérification détecte la corruption."""
    conn = create_test_db()
    for i in range(5):
        log_action(conn, user_id=i, action='LOGIN', detail='test', amount=0)
    # Altérer l'entrée id=3
    conn.execute("UPDATE audit_log SET action='HACK' WHERE id=3")
    conn.commit()
    ok, bad_id = verify_audit_chain(conn)
    assert ok == False
    assert bad_id == 3

def test_first_entry_genesis():
    """La première entrée est liée au GENESIS."""
    conn = create_test_db()
    log_action(conn, user_id=1, action='LOGIN', detail='test', amount=0)
    row = conn.execute(
        'SELECT prev_hmac FROM audit_log ORDER BY id ASC LIMIT 1'
    ).fetchone()
    genesis = compute_hmac('GENESIS', '0', 0, 0, '')
    assert row[0] == genesis