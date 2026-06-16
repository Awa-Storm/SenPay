import os

# Variables directes pour les imports directs (routes.py, logger.py...)
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_dev_key')
MASTER_KEY  = os.environ.get('SENPAY_KEY', 'test_master_key_32_bytes_1111111111')
DB_PATH     = os.environ.get('DB_PATH', 'senpay.db')

# Classe Config pour Flask 
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback_dev_key')
    MASTER_KEY = os.environ.get('SENPAY_KEY', 'test_master_key_32_bytes_1111111111')
    DB_PATH = os.environ.get('DB_PATH', 'senpay.db')

# Pour compatibilité avec les imports directs 
DB_PATH = Config.DB_PATH
SECRET_KEY = Config.SECRET_KEY
MASTER_KEY = Config.MASTER_KEY
