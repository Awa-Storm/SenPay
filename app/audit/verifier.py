import hmac
import hashlib
from app.audit.logger import compute_hmac

def verify_audit_chain(conn):
    """Parcourt audit_log et vérifie chaque HMAC enchaîné.
    Retourne (True, None) ou (False, id_premiere_entree_corrompue)."""
    rows = conn.execute(
        'SELECT id, user_id, action, detail, amount, timestamp, hmac, prev_hmac'
        ' FROM audit_log ORDER BY id ASC'
    ).fetchall()
    
    if not rows:
        return True, None
    
    for row in rows:
        id_, uid, action, detail, amount, ts, stored_hmac, prev_hmac = row
        expected = compute_hmac(action, ts, uid, amount or 0, prev_hmac)
        if not hmac.compare_digest(expected, stored_hmac):
            return False, id_
    return True, None

def compute_tx_hash(sender_id, receiver_id, amount, tx_type, ts, prev_tx_hash):
    """Calcule le hash SHA-256 d'une transaction."""
    payload = f'{sender_id}|{receiver_id}|{float(amount)}|{tx_type}|{ts}|{prev_tx_hash}'
    return hashlib.sha256(payload.encode()).hexdigest()

def verify_tx_chain(conn):
    """Parcourt transactions et vérifie chaque hash SHA-256 enchaîné.
    Retourne (True, None) ou (False, id_premiere_transaction_corrompue)."""
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