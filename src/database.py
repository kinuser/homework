from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

async_engine = create_async_engine(f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", echo=True)
Session = async_sessionmaker(async_engine)
