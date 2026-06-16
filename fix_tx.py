import sqlite3
conn = sqlite3.connect('senpay.db')
conn.execute('UPDATE transactions SET prev_tx_hash = "GENESIS" WHERE id = 1 AND prev_tx_hash IS NULL')
conn.commit()
print('Transaction #1 corrigee (prev_tx_hash = GENESIS)')
conn.close()
