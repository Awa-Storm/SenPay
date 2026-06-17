import hmac as hmac_lib
import hashlib
import os
from app.audit.logger import compute_hmac, derive_audit_key


def verify_audit_chain(conn) -> tuple:
    """Vérifie l'intégrité complète du journal d'audit"""
    
    key = derive_audit_key(os.environ.get('SENPAY_KEY'))
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, user_id, action, timestamp, amount, hmac, prev_hmac
           FROM audit_log ORDER BY id ASC"""
    )
    rows = cursor.fetchall()
    
    if not rows:
        return True, None
    
    # Vérifie que la première entrée part bien de GENESIS
    genesis_hmac = hmac_lib.new(key, b'GENESIS', hashlib.sha256).hexdigest()
    if rows[0][6] != genesis_hmac:
        return False, rows[0][0]
    
    for i, row in enumerate(rows):
        id_, user_id, action, ts, amount, stored_hmac, prev_hmac = row
        expected = compute_hmac(action, ts, user_id, amount, prev_hmac)
        if not hmac_lib.compare_digest(expected, stored_hmac):
            return False, id_
        if i > 0 and prev_hmac != rows[i - 1][5]:
            return False, id_
    
    return True, None


def compute_tx_hash(sender_id, receiver_id, amount, tx_type, ts, prev_tx_hash):
    """Calcule le hash SHA-256 d'une transaction — utilisé par Serigne"""
    payload = f'{sender_id}|{receiver_id}|{float(amount)}|{tx_type}|{ts}|{prev_tx_hash}'
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_tx_chain(conn) -> tuple:
    """Vérifie l'intégrité de la chaîne de transactions — utilisé par Serigne"""
    rows = conn.execute(
        'SELECT id, sender_id, receiver_id, amount, tx_type, created_at, tx_hash, prev_tx_hash'
        ' FROM transactions ORDER BY id ASC'
    ).fetchall()
    
    if not rows:
        return True, None
    
    for row in rows:
        id_, sender, receiver, amount, tx_type, ts, stored_hash, prev_hash = row
        expected = compute_tx_hash(sender, receiver, amount, tx_type, ts, prev_hash or '')
        if expected != stored_hash:
            return False, id_
    
    return True, None
