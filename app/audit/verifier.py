<<<<<<< HEAD
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
=======
import hmac as hmac_lib
import hashlib
import os
from app.audit.logger import compute_hmac, derive_audit_key


def verify_audit_chain(conn) -> tuple:
    """Vérifie l'intégrité complète du journal d'audit
    
    Relit toutes les entrées dans l'ordre et recalcule chaque empreinte.
    Si une entrée a été modifiée, son empreinte ne correspondra plus.
    
    Paramètres :
        conn → connexion SQLite active
        
    Retourne :
        (True, None)  → journal intact, aucune falsification détectée
        (False, id)   → falsification détectée, id = première entrée corrompue
    """
    
    # Récupère la clé audit depuis l'environnement
    key = derive_audit_key(os.environ.get('SENPAY_KEY'))
    
    cursor = conn.cursor()
    
    # Récupère toutes les entrées dans l'ordre chronologique
    cursor.execute(
        """SELECT id, user_id, action, timestamp, amount, hmac, prev_hmac
           FROM audit_log ORDER BY id ASC"""
    )
    rows = cursor.fetchall()
    
    # Journal vide : rien à vérifier, c'est considéré comme intact
    if not rows:
        return True, None
    
    # Vérifie que la première entrée part bien de GENESIS
    # Si ce n'est pas le cas → la première entrée a été falsifiée
    genesis_hmac = hmac_lib.new(key, b'GENESIS', hashlib.sha256).hexdigest()
    if rows[0][6] != genesis_hmac:
        return False, rows[0][0]
    
    # Parcourt toutes les entrées une par une
    for i, row in enumerate(rows):
        id_, user_id, action, ts, amount, stored_hmac, prev_hmac = row
        
        # Recalcule l'empreinte attendue avec les données stockées
        expected = compute_hmac(action, ts, user_id, amount, prev_hmac)
        
        # Compare de façon sécurisée (compare_digest évite les attaques temporelles)
        # Si les empreintes diffèrent → cette entrée a été modifiée
        if not hmac_lib.compare_digest(expected, stored_hmac):
            return False, id_
        
        # Vérifie aussi que le prev_hmac correspond bien au hmac de l'entrée précédente
        # Empêche qu'on réordonne ou supprime des entrées au milieu
        if i > 0 and prev_hmac != rows[i - 1][5]:
            return False, id_
    
    # Toutes les entrées sont intactes
    return True, None
>>>>>>> origin/main
