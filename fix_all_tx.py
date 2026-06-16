import sqlite3
from app.transactions.tx import compute_tx_hash

conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row

transactions = conn.execute('SELECT id, sender_id, receiver_id, amount, tx_type, timestamp, prev_tx_hash FROM transactions ORDER BY id').fetchall()

for tx in transactions:
    new_hash = compute_tx_hash(
        tx['sender_id'], tx['receiver_id'], tx['amount'],
        tx['tx_type'], tx['timestamp'], tx['prev_tx_hash']
    )
    conn.execute('UPDATE transactions SET tx_hash = ? WHERE id = ?', (new_hash, tx['id']))
    print(f'Transaction #{tx["id"]} mise à jour')

conn.commit()
print('Toutes les transactions ont été corrigées')
conn.close()
