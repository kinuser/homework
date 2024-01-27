from src.database import async_engine
from src.models import Base
import pytest


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def create_database(anyio_backend):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('\nCreate tables')
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print('\nDelete tables')