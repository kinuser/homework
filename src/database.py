"""Database init"""
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

async_engine = create_async_engine(
    f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}', echo=False)
Session = async_sessionmaker(async_engine)
