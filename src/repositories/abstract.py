from abc import ABC, abstractmethod

from sqlalchemy import Table
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class AbstractRepository(ABC):
    def __init__(self, table: Table, session: async_sessionmaker[AsyncSession]):
        self.table = table
        self.session = session

    @abstractmethod
    async def create_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, *args, **kwargs):
        raise NotImplementedError