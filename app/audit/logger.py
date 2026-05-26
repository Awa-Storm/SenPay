import hmac
import hashlib
from datetime import datetime
from app.crypto.keys import AUDIT_KEY

def compute_hmac(action, timestamp, user_id, amount, prev_hmac):
    """Calcule le HMAC enchaîné d'une entrée d'audit."""
    payload = f'{action}|{timestamp}|{user_id}|{amount}|{prev_hmac}'.encode()
    return hmac.new(AUDIT_KEY, payload, hashlib.sha256).hexdigest()

def log_action(conn, user_id, action, detail=None, amount=None):
    """Insère une entrée dans audit_log avec HMAC enchaîné."""
    # Récupérer le HMAC précédent
    prev = conn.execute(
        'SELECT hmac FROM audit_log ORDER BY id DESC LIMIT 1'
    ).fetchone()
    
    # Si première entrée → GENESIS
    prev_hmac = prev[0] if prev else compute_hmac('GENESIS', '0', 0, 0, '')
    
    # Horodatage UTC
    ts = datetime.utcnow().isoformat() + 'Z'
    
    # Calculer le HMAC de cette entrée
    h = compute_hmac(action, ts, user_id, amount or 0, prev_hmac)
    
    # Insérer dans la base de données
    conn.execute(
        'INSERT INTO audit_log(user_id, action, detail, amount, timestamp, hmac, prev_hmac)'
        ' VALUES(?, ?, ?, ?, ?, ?, ?)',
        (user_id, action, detail, amount, ts, h, prev_hmac)
    )
    conn.commit()