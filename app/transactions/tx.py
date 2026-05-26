import hashlib

def compute_tx_hash(sender_id, receiver_id, amount, tx_type, timestamp, prev_tx_hash):
    """
    Calcule le hash SHA-256 d'une transaction pour assurer l'intégrité de la chaîne.
    """
    prev = prev_tx_hash if prev_tx_hash else "GENESIS"
    data = f"{sender_id}|{receiver_id}|{amount}|{tx_type}|{timestamp}|{prev}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()