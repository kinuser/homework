from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update, and_
from sqlalchemy.exc import IntegrityError, NoResultFound
from models import submenu_table, menu_table
from repositories.abstract import AbstractRepository
from uuid import UUID


class DishRepository(AbstractRepository):

    async def create_one(self, value: dict, sm_id: UUID):
        value['submenu_id'] = sm_id
        stmt = insert(self.table).values(**value).returning(self.table)
        async with self.session() as session:
            try:
                result = await session.execute(stmt)
                await session.commit()
                return result.first()._asdict()
            except IntegrityError:
                return None

    async def get_all(self, sm_id: UUID):
        query = select(self.table).where(self.table.c.submenu_id == sm_id)
        async with self.session() as session:
            result = await session.execute(query)
            return [x._asdict() for x in result.all()]

    async def get_one(self, d_id: UUID):
        query = select(self.table).filter_by(id=d_id)
        async with self.session() as session:
            try:
                result = await session.execute(query)
                return result.first()._asdict()
            except (NoResultFound, AttributeError):
                return None

    async def delete_one(self, d_id: UUID):
        stmt = delete(self.table).where(self.table.c.id == d_id)
        async with self.session() as session:
            try:
                result = await session.execute(stmt)
                await session.commit()
                return True
            except IntegrityError:
                return None

    async def update_one(self, value: dict, d_id: UUID):
        stmt = update(self.table).values(**value).where(self.table.c.id == d_id).returning(self.table)
        async with self.session() as session:
            result = await session.execute(stmt)
            await session.commit()
            try:
                return result.first()._asdict()
            except IntegrityError:
                return None
