from app.crypto.aes import decrypt_balance
import sqlite3
import traceback

conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row
user = conn.execute('SELECT balance_enc, balance_iv, balance_tag FROM users WHERE phone=771234568').fetchone()

print(f'enc={user["balance_enc"]}')
print(f'iv={user["balance_iv"]}')
print(f'tag={user["balance_tag"]}')

try:
    bal = decrypt_balance(user['balance_enc'], user['balance_iv'], user['balance_tag'])
    print(f'Solde dechiffre: {bal}')
except Exception as e:
    print(f'Erreur: {e}')
    traceback.print_exc()

conn.close()
