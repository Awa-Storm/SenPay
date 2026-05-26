import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Clé maître depuis variable d'environnement
MASTER_KEY = os.environ.get('SENPAY_MASTER_KEY', '').encode()

# Dérivation de la clé pour les soldes (AES-256-GCM)
BALANCE_KEY = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'senpay-balance'
).derive(MASTER_KEY)

# Dérivation de la clé pour l'audit (HMAC)
AUDIT_KEY = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'senpay-audit'
).derive(MASTER_KEY)