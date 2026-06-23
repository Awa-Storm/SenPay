import os
import sqlite3
import pytest

os.environ.setdefault('SENPAY_KEY', 'a' * 64)

from app.audit.logger import log_action, derive_audit_key, get_genesis_hmac
from app.audit.verifier import verify_audit_chain


def make_db():
    conn = sqlite3.connect(':memory:')
    conn.executescript("""
        CREATE TABLE audit_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER,
            action    TEXT NOT NULL,
            detail    TEXT,
            amount    REAL DEFAULT 0,
            timestamp TEXT NOT NULL,
            hmac      TEXT NOT NULL,
            prev_hmac TEXT
        );
    """)
    return conn


def test_hmac_chain_valid():
    """Chaîne de 100 entrées doit être intacte"""
    conn = make_db()
    for i in range(100):
        log_action(conn, user_id=1, action=f'ACTION_{i}', amount=float(i))
    valid, bad_id = verify_audit_chain(conn)
    assert valid is True
    assert bad_id is None
    conn.close()


def test_hmac_chain_tampered():
    """Modification d'une entrée doit être détectée"""
    conn = make_db()
    for i in range(60):
        log_action(conn, user_id=1, action=f'ACTION_{i}', amount=float(i))
    conn.execute("UPDATE audit_log SET amount=9999.0 WHERE id=50")
    conn.commit()
    valid, bad_id = verify_audit_chain(conn)
    assert valid is False
    assert bad_id is not None
    conn.close()


def test_first_entry_genesis():
    """Le prev_hmac de la première entrée doit être GENESIS"""
    import hmac, hashlib
    conn = make_db()
    log_action(conn, user_id=1, action='LOGIN_SUCCESS')
    cur = conn.cursor()
    cur.execute("SELECT prev_hmac FROM audit_log ORDER BY id ASC LIMIT 1")
    row = cur.fetchone()
    key = derive_audit_key(os.environ['SENPAY_KEY'])
    genesis = hmac.new(key, b'GENESIS', hashlib.sha256).hexdigest()
    assert row[0] == genesis
    conn.close()
