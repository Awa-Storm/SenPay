import pytest
import sqlite3
from datetime import datetime
from app.transactions.tx import compute_tx_hash
from app.transactions.verifier import verify_tx_chain

@pytest.fixture
def db_with_transactions():
    """Crée une base SQLite en mémoire avec 50 transactions intègres."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER, receiver_id INTEGER,
            amount REAL, tx_type TEXT,
            timestamp TEXT, tx_hash TEXT, prev_tx_hash TEXT
        )
    """)
    prev = None
    for i in range(50):
        ts = datetime.utcnow().isoformat()
        h = compute_tx_hash(1, 2, 1000.0 + i, 'TRANSFER', ts, prev)
        conn.execute(
            "INSERT INTO transactions VALUES (NULL,1,2,?,?,?,?,?)",
            (1000.0 + i, 'TRANSFER', ts, h, prev)
        )
        prev = h
    conn.commit()
    return conn

def test_tx_hash_valid(db_with_transactions):
    """50 transactions intègres → vérification réussie."""
    ok, err_id = verify_tx_chain(db_with_transactions)
    assert ok is True
    assert err_id is None

def test_tx_hash_tampered(db_with_transactions):
    """Modification d'un montant → détection immédiate."""
    # Altérer la transaction #25
    db_with_transactions.execute(
        "UPDATE transactions SET amount = 99999.0 WHERE id = 25"
    )
    db_with_transactions.commit()
    ok, err_id = verify_tx_chain(db_with_transactions)
    assert ok is False
    assert err_id is not None