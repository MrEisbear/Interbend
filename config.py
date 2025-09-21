import os
from dotenv import load_dotenv

# Find the absolute path of the root directory
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # General Config
    JWT_KEY = os.getenv('JWT_KEY')
    JWT_EXPIRE = int(os.getenv('JWT_EXPIRATION', 30))

    # Database
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    # Admin
    ADMIN_KEY = os.getenv('ADMIN_KEY')
    COLLECT_COOLDOWN = int(os.getenv('COLLECT_COOLDOWN', 24))
    TAX_ACCOUNT_BID = os.getenv('TAX_ACCOUNT_BID')