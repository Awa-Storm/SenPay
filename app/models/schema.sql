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
    force_pin_change INTEGER NOT NULL DEFAULT 0,  -- EF11 : changement PIN obligatoire
    last_login      TEXT                           -- horodatage dernière connexion
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
-- Table des transactions avec chaînage SHA-256
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    receiver_id INTEGER NOT NULL REFERENCES users(id),
    amount REAL NOT NULL CHECK(amount > 0),
    tx_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    tx_hash TEXT NOT NULL UNIQUE,
    prev_tx_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Table du journal d'audit avec chaînage HMAC
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL,
    detail TEXT,
    amount REAL,
    timestamp TEXT NOT NULL,
    hmac TEXT NOT NULL,
    prev_hmac TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);


-- Table des sessions actives — remplace les sessions Flask du Sprint Alpha
-- Le token est la clé primaire : unique, impossible à deviner (32 octets CSPRNG)
CREATE TABLE IF NOT EXISTS sessions (
    token            TEXT PRIMARY KEY,
    user_id          INTEGER NOT NULL REFERENCES users(id),
    role             TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    expires_at       TEXT NOT NULL,
    force_pin_change INTEGER NOT NULL DEFAULT 0
);
