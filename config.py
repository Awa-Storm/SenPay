import os

# Variables directes pour les imports directs (routes.py, logger.py...)
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_dev_key')
MASTER_KEY  = os.environ.get('SENPAY_KEY', 'test_master_key_32_bytes_1111111111')
DB_PATH     = os.environ.get('DB_PATH', 'senpay.db')

# Classe Config pour Flask (utilisée par app/__init__.py de Serigne)
class Config:
    SECRET_KEY = SECRET_KEY
    MASTER_KEY = MASTER_KEY
    DB_PATH    = DB_PATH