import sqlite3
conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row
users = conn.execute('SELECT id, phone, balance_enc, balance_iv, balance_tag FROM users').fetchall()
for u in users:
    print(f"{u['id']} | {u['phone']} | enc={u['balance_enc'][:20] if u['balance_enc'] else 'None'}...")
conn.close()
