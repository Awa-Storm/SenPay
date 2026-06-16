from app.crypto.aes import encrypt_balance
import sqlite3

conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row
users = conn.execute('SELECT id FROM users').fetchall()

for user in users:
    enc, iv, tag = encrypt_balance(100000.0)
    conn.execute('UPDATE users SET balance_enc=?, balance_iv=?, balance_tag=? WHERE id=?',
                 (enc, iv, tag, user['id']))
    print(f'User {user["id"]} mis a jour')

conn.commit()
conn.close()
print('Tous les soldes ont ete rechiffres avec la bonne clé')
