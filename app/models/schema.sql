CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    pin_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'client',
    balance_enc TEXT,
    balance_iv TEXT,
    balance_tag TEXT,
    is_locked INTEGER DEFAULT 0,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER REFERENCES users(id),
    receiver_id INTEGER REFERENCES users(id),
    amount REAL NOT NULL,
    tx_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    tx_hash TEXT NOT NULL,
    prev_tx_hash TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL,
    detail TEXT,
    amount REAL,
    timestamp TEXT NOT NULL,
    hmac TEXT NOT NULL,
    prev_hmac TEXT
);
