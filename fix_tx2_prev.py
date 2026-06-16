import sqlite3
conn = sqlite3.connect('senpay.db')

# Récupérer le hash de la transaction #1
r = conn.execute('SELECT tx_hash FROM transactions WHERE id = 1').fetchone()
hash1 = r[0]

# Mettre à jour la transaction #2
conn.execute('UPDATE transactions SET prev_tx_hash = ? WHERE id = 2', (hash1,))
conn.commit()

print(f'Transaction #2 corrigée: prev_tx_hash = {hash1}')

conn.close()
