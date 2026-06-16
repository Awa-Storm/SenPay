import sqlite3
from app.transactions.tx import compute_tx_hash

conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row

# Récupérer la transaction #1
tx = conn.execute('SELECT id, sender_id, receiver_id, amount, tx_type, timestamp, prev_tx_hash FROM transactions WHERE id = 1').fetchone()

# Recalculer le hash
new_hash = compute_tx_hash(
    tx['sender_id'], tx['receiver_id'], tx['amount'],
    tx['tx_type'], tx['timestamp'], tx['prev_tx_hash']
)

# Mettre à jour
conn.execute('UPDATE transactions SET tx_hash = ? WHERE id = 1', (new_hash,))
conn.commit()
print(f'Transaction #1 mise à jour avec hash: {new_hash[:16]}...')
conn.close()
