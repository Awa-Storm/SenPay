import bcrypt

def hash_pin(pin_str):
    """Hache un code PIN avec bcrypt cost=12."""
    pin_bytes = pin_str.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pin_bytes, salt)
    return hashed.decode('utf-8')

def verify_pin(pin_str, stored_hash):
    """Vérifie un PIN contre son hash bcrypt stocké."""
    pin_bytes = pin_str.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    return bcrypt.checkpw(pin_bytes, hash_bytes)