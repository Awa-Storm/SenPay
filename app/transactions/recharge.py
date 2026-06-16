import sqlite3
from datetime import datetime, timezone

def execute_recharge(conn, agent_id, client_phone, amount):
    '''
    Recharge un compte client (agent ou admin).
    Retourne (True, message) ou (False, message_erreur).
    '''
    try:
        # Verifier que le client existe
        client = conn.execute(
            'SELECT id, is_locked FROM users WHERE phone = ? AND role = "client"',
            (client_phone,)
        ).fetchone()
        
        if not client:
            return False, 'Client introuvable'
        
        if client['is_locked']:
            return False, 'Compte client verrouille'
        
        # Verifier montant
        if amount <= 0:
            return False, 'Montant invalide'
        
        # Insertion dans transactions (recharge)
        ts = datetime.now(timezone.utc).isoformat()
        conn.execute(
            'INSERT INTO transactions (sender_id, receiver_id, amount, tx_type, timestamp, tx_hash, prev_tx_hash) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (agent_id, client['id'], amount, 'recharge', ts, 'hash_recharge', None)
        )
        conn.commit()
        
        return True, f'Recharge de {amount} FCFA effectuee pour {client_phone}'
        
    except Exception as e:
        return False, f'Erreur interne: {str(e)}'
