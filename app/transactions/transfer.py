import sqlite3
from datetime import datetime, timezone
from app.transactions.tx import compute_tx_hash
from app.crypto.aes import encrypt_balance, decrypt_balance

MAX_TX_AMOUNT = 500_000
MIN_TX_AMOUNT = 100
DAILY_LIMIT = 2_000_000

def execute_transfer(conn, sender_id, receiver_phone, amount):
    if not (MIN_TX_AMOUNT <= amount <= MAX_TX_AMOUNT):
        return False, f'Montant hors limites ({MIN_TX_AMOUNT} - {MAX_TX_AMOUNT} FCFA)'
    
    try:
        conn.execute('BEGIN IMMEDIATE')
        
        recv = conn.execute(
            'SELECT id, is_locked FROM users WHERE phone = ?',
            (receiver_phone,)
        ).fetchone()
        
        if not recv:
            conn.execute('ROLLBACK')
            return False, 'Destinataire introuvable'
        
        if recv['is_locked']:
            conn.execute('ROLLBACK')
            return False, 'Compte destinataire verrouille'
        
        if recv['id'] == sender_id:
            conn.execute('ROLLBACK')
            return False, 'Auto-transfert interdit'
        
        # Limite journaliere
        today = datetime.now(timezone.utc).date().isoformat()
        daily = conn.execute(
            'SELECT COALESCE(SUM(amount), 0) FROM transactions '
            'WHERE sender_id = ? AND DATE(timestamp) = ? AND tx_type = "transfer"',
            (sender_id, today)
        ).fetchone()[0]
        
        if daily + amount > DAILY_LIMIT:
            conn.execute('ROLLBACK')
            return False, f'Limite journaliere de {DAILY_LIMIT} FCFA atteinte'
        
        # Dechiffrer soldes
        sndr = conn.execute(
            'SELECT balance_enc, balance_iv, balance_tag FROM users WHERE id = ?',
            (sender_id,)
        ).fetchone()
        bal_s = decrypt_balance(sndr['balance_enc'], sndr['balance_iv'], sndr['balance_tag'])
        
        if bal_s < amount:
            conn.execute('ROLLBACK')
            return False, 'Solde insuffisant'
        
        recv_data = conn.execute(
            'SELECT balance_enc, balance_iv, balance_tag FROM users WHERE id = ?',
            (recv['id'],)
        ).fetchone()
        bal_r = decrypt_balance(recv_data['balance_enc'], recv_data['balance_iv'], recv_data['balance_tag'])
        
        # Nouveaux soldes
        new_s = bal_s - amount
        new_r = bal_r + amount
        
        # Chiffrer
        enc_s, iv_s, tag_s = encrypt_balance(new_s)
        enc_r, iv_r, tag_r = encrypt_balance(new_r)
        
        # Mise a jour
        conn.execute(
            'UPDATE users SET balance_enc=?, balance_iv=?, balance_tag=? WHERE id=?',
            (enc_s, iv_s, tag_s, sender_id)
        )
        conn.execute(
            'UPDATE users SET balance_enc=?, balance_iv=?, balance_tag=? WHERE id=?',
            (enc_r, iv_r, tag_r, recv['id'])
        )
        
        # Chainage SHA-256
        prev = conn.execute('SELECT tx_hash FROM transactions ORDER BY id DESC LIMIT 1').fetchone()
        prev_hash = prev['tx_hash'] if prev else 'GENESIS'
        ts = datetime.now(timezone.utc).isoformat()
        tx_hash = compute_tx_hash(sender_id, recv['id'], amount, 'transfer', ts, prev_hash)
        
        conn.execute(
            'INSERT INTO transactions (sender_id, receiver_id, amount, tx_type, timestamp, tx_hash, prev_tx_hash) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (sender_id, recv['id'], amount, 'transfer', ts, tx_hash, prev_hash)
        )
        
        conn.execute('COMMIT')
        return True, tx_hash
        
    except Exception as e:
        conn.execute('ROLLBACK')
        return False, f'Erreur interne: {str(e)}'
