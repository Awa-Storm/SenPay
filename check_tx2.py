import sqlite3
conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row
tx = conn.execute('SELECT id, sender_id, receiver_id, amount, tx_type, timestamp, prev_tx_hash, tx_hash FROM transactions WHERE id = 2').fetchone()
print(f"id={tx['id']}")
print(f"sender={tx['sender_id']}")
print(f"receiver={tx['receiver_id']}")
print(f"amount={tx['amount']}")
print(f"tx_type={tx['tx_type']}")
print(f"timestamp={tx['timestamp']}")
print(f"prev_tx_hash={tx['prev_tx_hash']}")
print(f"tx_hash={tx['tx_hash']}")
conn.close()
