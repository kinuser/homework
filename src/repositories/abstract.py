from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class AbstractRepository(ABC):
    def __init__(self, orm: Any, session: async_sessionmaker[AsyncSession]):
        self.orm = orm
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
