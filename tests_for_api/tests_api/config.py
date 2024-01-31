import os
import dotenv

dotenv.load_dotenv()

APP_HOST = os.environ.get('APP_HOST')
APP_PORT = os.environ.get('APP_PORT')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')