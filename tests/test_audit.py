import os
import sqlite3
import pytest

# Clé de test : 64 caractères hex = 32 octets
# On la définit AVANT d'importer les modules qui en ont besoin
os.environ['SENPAY_KEY'] = 'a' * 64

from app.audit.logger import log_action, derive_audit_key, get_genesis_hmac
from app.audit.verifier import verify_audit_chain


def make_db():
    """Crée une base SQLite en mémoire avec la table audit_log
    
    ':memory:' → la base est temporaire, elle disparaît après le test.
    Chaque test repart d'une base propre et vide.
    """
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
        
        CREATE TABLE users (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            phone          TEXT UNIQUE NOT NULL,
            pin_hash       TEXT NOT NULL,
            role           TEXT NOT NULL DEFAULT 'client',
            balance_enc    TEXT,
            balance_iv     TEXT,
            balance_tag    TEXT,
            is_locked      INTEGER DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0,
            locked_until   TEXT
        );
    """)
    return conn


def test_hmac_chain_valid():
    """Test 1 : une chaîne de 100 entrées doit être considérée intacte"""
    
    conn = make_db()
    
    # Crée 100 entrées dans le journal
    for i in range(100):
        log_action(conn, user_id=1, action=f'ACTION_{i}', amount=float(i))
    
    # Vérifie l'intégrité de toute la chaîne
    valid, bad_id = verify_audit_chain(conn)
    
    # Résultat attendu : chaîne valide, aucune entrée corrompue
    assert valid is True
    assert bad_id is None
    
    conn.close()


def test_hmac_chain_tampered():
    """Test 2 : modifier une entrée doit être immédiatement détecté"""
    
    conn = make_db()
    
    # Crée 60 entrées normales
    for i in range(60):
        log_action(conn, user_id=1, action=f'ACTION_{i}', amount=float(i))
    
    # Falsifie l'entrée #50 : change le montant directement en base
    # C'est ce qu'un attaquant ferait pour dissimuler une transaction
    conn.execute("UPDATE audit_log SET amount=9999.0 WHERE id=50")
    conn.commit()
    
    # Vérifie l'intégrité : doit détecter la falsification
    valid, bad_id = verify_audit_chain(conn)
    
    # Résultat attendu : chaîne invalide, id de l'entrée corrompue retourné
    assert valid is False
    assert bad_id is not None
    
    conn.close()


def test_first_entry_genesis():
    """Test 3 : le prev_hmac de la première entrée doit être GENESIS"""
    
    import hmac
    import hashlib
    
    conn = make_db()
    
    # Crée une seule entrée dans le journal vide
    log_action(conn, user_id=1, action='LOGIN_SUCCESS')
    
    # Récupère le prev_hmac de la première entrée
    cur = conn.cursor()
    cur.execute(
        "SELECT prev_hmac FROM audit_log ORDER BY id ASC LIMIT 1"
    )
    row = cur.fetchone()
    
    # Recalcule GENESIS indépendamment
    key = derive_audit_key(os.environ['SENPAY_KEY'])
    expected_genesis = hmac.new(key, b'GENESIS', hashlib.sha256).hexdigest()
    
    # Le prev_hmac stocké doit correspondre exactement à GENESIS
    assert row[0] == expected_genesis
    
    conn.close()
