import sqlite3
from app.transactions.tx import compute_tx_hash

conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row

# Récupérer le hash de la transaction #1
r = conn.execute('SELECT tx_hash FROM transactions WHERE id = 1').fetchone()
hash1 = r[0]
print(f'Hash de la transaction #1: {hash1}')

# Mettre à jour la transaction #2
conn.execute('UPDATE transactions SET prev_tx_hash = ? WHERE id = 2', (hash1,))
conn.commit()

# Vérifier que prev_tx_hash a bien été mis à jour
r2 = conn.execute('SELECT prev_tx_hash FROM transactions WHERE id = 2').fetchone()
print(f'prev_tx_hash après mise à jour: {r2[0]}')

# Recalculer le hash de la transaction #2
tx = conn.execute('SELECT id, sender_id, receiver_id, amount, tx_type, timestamp, prev_tx_hash FROM transactions WHERE id = 2').fetchone()
new_hash = compute_tx_hash(
    tx['sender_id'], tx['receiver_id'], tx['amount'],
    tx['tx_type'], tx['timestamp'], tx['prev_tx_hash']
)
print(f'Nouveau hash calculé: {new_hash}')

# Mettre à jour tx_hash
conn.execute('UPDATE transactions SET tx_hash = ? WHERE id = 2', (new_hash,))
conn.commit()

# Vérification finale
tx2 = conn.execute('SELECT prev_tx_hash, tx_hash FROM transactions WHERE id = 2').fetchone()
print(f'--- APRES CORRECTION ---')
print(f'prev_tx_hash: {tx2[0]}')
print(f'tx_hash: {tx2[1]}')

conn.close()
