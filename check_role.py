import sqlite3
conn = sqlite3.connect('senpay.db')
conn.row_factory = sqlite3.Row
user = conn.execute('SELECT id, phone, role FROM users WHERE phone=771234567').fetchone()
print(f'Role: {user["role"]}')
conn.close()
