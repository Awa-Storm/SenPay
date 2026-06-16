import sqlite3
from app.transactions.tx import compute_tx_hash

conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row

# Récupérer la transaction #2
tx = conn.execute('SELECT id, sender_id, receiver_id, amount, tx_type, timestamp, prev_tx_hash FROM transactions WHERE id = 2').fetchone()

if tx:
    new_hash = compute_tx_hash(
        tx['sender_id'], tx['receiver_id'], tx['amount'],
        tx['tx_type'], tx['timestamp'], tx['prev_tx_hash']
    )
    conn.execute('UPDATE transactions SET tx_hash = ? WHERE id = 2', (new_hash,))
    conn.commit()
    print(f'Transaction #2 mise à jour avec hash: {new_hash[:16]}...')
else:
    print('Transaction #2 non trouvée')

conn.close()
