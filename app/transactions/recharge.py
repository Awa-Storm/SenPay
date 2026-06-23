import sqlite3
from datetime import datetime, timezone
from app.crypto.aes import encrypt_balance, decrypt_balance

def execute_recharge(conn, agent_id, client_phone, amount):
    '''
    Recharge un compte client (agent ou admin).
    Retourne (True, message) ou (False, message_erreur).
    '''
    try:
        # Vérifier que le client existe
        client = conn.execute(
            'SELECT id, balance_enc, balance_iv, balance_tag, is_locked FROM users WHERE phone = ? AND role = "client"',
            (client_phone,)
        ).fetchone()

        if not client:
            return False, 'Client introuvable'

        if client['is_locked']:
            return False, 'Compte client verrouillé'

        if amount <= 0:
            return False, 'Montant invalide'

        # Déchiffrer le solde actuel du client
        try:
            current_balance = decrypt_balance(
                client['balance_enc'],
                client['balance_iv'],
                client['balance_tag']
            )
        except:
            current_balance = 0.0

        # Nouveau solde
        new_balance = current_balance + amount

        # Chiffrer le nouveau solde
        enc, iv, tag = encrypt_balance(new_balance)

        # Mettre à jour le solde du client
        conn.execute(
            'UPDATE users SET balance_enc = ?, balance_iv = ?, balance_tag = ? WHERE id = ?',
            (enc, iv, tag, client['id'])
        )

        # Insertion dans transactions (recharge)
        ts = datetime.now(timezone.utc).isoformat()
        conn.execute(
            'INSERT INTO transactions (sender_id, receiver_id, amount, tx_type, timestamp, tx_hash, prev_tx_hash) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (agent_id, client['id'], amount, 'recharge', ts, 'hash_recharge', None)
        )

        conn.commit()
        return True, f'Recharge de {amount} FCFA effectuée pour {client_phone}'

    except Exception as e:
        conn.execute('ROLLBACK')
        return False, f'Erreur interne: {str(e)}'
