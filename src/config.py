"""Config file"""
import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
RED_PORT = os.environ.get('RED_PORT')
RED_HOST = os.environ.get('RED_HOST')
RAB_HOST = os.environ.get('RAB_HOST')
RAB_PORT = os.environ.get('RAB_PORT')
SHEET_URL = os.environ.get('SHEET_URL')
