import os
import sqlite3
import time
import pytest

os.environ.setdefault('SENPAY_KEY', 'a' * 64)
os.environ.setdefault('SECRET_KEY', os.urandom(32).hex())

from app.auth.authenticator import hash_pin, verify_pin, authenticate, BCRYPT_COST, MAX_ATTEMPTS, LOCK_MINUTES
from app.auth.session_mgr import create_session, validate_session, revoke_session


def make_db():
    """Base SQLite en mémoire avec tables users et sessions"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE users (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            phone            TEXT UNIQUE NOT NULL,
            pin_hash         TEXT NOT NULL,
            role             TEXT NOT NULL DEFAULT 'client',
            balance_enc      TEXT,
            balance_iv       TEXT,
            balance_tag      TEXT,
            is_locked        INTEGER DEFAULT 0,
            failed_attempts  INTEGER DEFAULT 0,
            locked_until     TEXT,
            force_pin_change INTEGER NOT NULL DEFAULT 0,
            last_login       TEXT
        );
        CREATE TABLE sessions (
            token            TEXT PRIMARY KEY,
            user_id          INTEGER NOT NULL REFERENCES users(id),
            role             TEXT NOT NULL,
            created_at       TEXT NOT NULL,
            expires_at       TEXT NOT NULL,
            force_pin_change INTEGER NOT NULL DEFAULT 0
        );
    """)
    return conn


def insert_user(conn, phone='771234567', pin='1234', role='client',
                locked=0, attempts=0, locked_until=None, force=0):
    """Insère un utilisateur de test en base"""
    pin_hash = hash_pin(pin)
    conn.execute(
        """INSERT INTO users
           (phone, pin_hash, role, is_locked, failed_attempts, locked_until, force_pin_change)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (phone, pin_hash, role, locked, attempts, locked_until, force)
    )
    conn.commit()


def test_bcrypt_cost12():
    """OS-01 : le hash doit utiliser bcrypt avec coût 12"""
    h = hash_pin('1234')
    # Le hash bcrypt encode le coût dans sa structure : $2b$12$...
    assert '$2b$12$' in h


def test_login_invalid_phone():
    """Numéro introuvable → retourne (None, 'invalid')"""
    conn = make_db()
    user, error = authenticate(conn, '700000000', '1234')
    assert user is None
    assert error == 'invalid'
    conn.close()


def test_login_invalid_pin():
    """PIN incorrect → retourne (None, 'invalid')"""
    conn = make_db()
    insert_user(conn)
    user, error = authenticate(conn, '771234567', '9999')
    assert user is None
    assert error == 'invalid'
    conn.close()


def test_lockout_after_3():
    """OS-07 : 3 échecs consécutifs → compte verrouillé"""
    conn = make_db()
    insert_user(conn)
    # 3 tentatives avec mauvais PIN
    for _ in range(3):
        authenticate(conn, '771234567', '0000')
    user, error = authenticate(conn, '771234567', '1234')
    assert error == 'locked'
    conn.close()


def test_lockout_auto_release():
    """OS-07 : verrouillage expiré → déverrouillage automatique"""
    from datetime import datetime, timedelta, timezone
    conn = make_db()
    # Insère un utilisateur déjà verrouillé avec expiration dans le passé
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    insert_user(conn, locked=1, attempts=3, locked_until=past)
    # Doit se déverrouiller automatiquement et accepter le bon PIN
    user, error = authenticate(conn, '771234567', '1234')
    assert error is None
    assert user is not None
    conn.close()


def test_force_pin_change():
    """EF11 : force_pin_change=1 → flag présent dans la session créée"""
    conn = make_db()
    insert_user(conn, force=1)
    user, error = authenticate(conn, '771234567', '1234')
    assert error is None
    # Crée la session avec force_pin_change
    token = create_session(conn, user[0], user[2], force_pin_change=1)
    sess = validate_session(conn, token)
    assert sess['force_pin_change'] == 1
    conn.close()


def test_session_token_entropy():
    """OS-05 : deux tokens générés doivent être différents"""
    conn = make_db()
    insert_user(conn, phone='771111111')
    insert_user(conn, phone='772222222')
    token1 = create_session(conn, 1, 'client')
    token2 = create_session(conn, 2, 'client')
    # Tokens différents — entropie de 256 bits garantit l'unicité
    assert token1 != token2
    # Longueur attendue : 64 caractères hex
    assert len(token1) == 64
    conn.close()


def test_session_expiry_30min():
    """EF02 : session expirée → validate_session retourne None"""
    from datetime import datetime, timedelta, timezone
    conn = make_db()
    insert_user(conn)
    token = create_session(conn, 1, 'client')
    # Force l'expiration dans le passé
    past = (datetime.now(timezone.utc) - timedelta(minutes=31)).isoformat()
    conn.execute('UPDATE sessions SET expires_at=? WHERE token=?', (past, token))
    conn.commit()
    # Session expirée → doit retourner None
    result = validate_session(conn, token)
    assert result is None
    conn.close()


def test_session_revoke_logout():
    """OS-05 : après révocation, le token devient inutilisable"""
    conn = make_db()
    insert_user(conn)
    token = create_session(conn, 1, 'client')
    # Révoque la session
    revoke_session(conn, token)
    # Token révoqué → validate_session doit retourner None
    result = validate_session(conn, token)
    assert result is None
    conn.close()
