from app.transactions.tx import compute_tx_hash

def verify_tx_chain(conn):
    """
    Parcourt toutes les transactions et recalcule chaque hash.
    Retourne (True, None) si intègre, (False, id_corrompu) sinon.
    """
    cursor = conn.execute(
        "SELECT id, sender_id, receiver_id, amount, tx_type, timestamp, tx_hash, prev_tx_hash "
        "FROM transactions ORDER BY id ASC"
    )
    transactions = cursor.fetchall()

    prev_hash = None
    for tx in transactions:
        expected = compute_tx_hash(
            tx['sender_id'],
            tx['receiver_id'],
            tx['amount'],
            tx['tx_type'],
            tx['timestamp'],
            prev_hash
        )
        if expected != tx['tx_hash']:
            return False, tx['id']
        prev_hash = tx['tx_hash']

    return True, None