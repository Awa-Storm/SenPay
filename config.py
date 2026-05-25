import os

MASTER_KEY = os.environ.get('SENPAY_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
DB_PATH = os.environ.get('DB_PATH', 'senpay.db')
