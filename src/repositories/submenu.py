from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update, and_, func
from sqlalchemy.exc import IntegrityError, NoResultFound
from models import dish_table, menu_table, get_one_submenu, get_all_submenu
from repositories.abstract import AbstractRepository
from uuid import UUID



class SubmenuRepository(AbstractRepository):

    async def create_one(self, value: dict, m_id: UUID):
        value['menu_id'] = m_id
        stmt = insert(self.table).values(**value).returning(self.table.c.id)
        async with self.session() as session:
            try:
                dict_id = (await session.execute(stmt)).first()._asdict()
                result = (await session.execute(get_one_submenu(dict_id['id']))).first()._asdict()
                await session.commit()
                return result
            except IntegrityError:
                return None

    async def get_all(self, m_id: UUID):
        async with self.session() as session:
            result = await session.execute(get_all_submenu())
            return [x._asdict() for x in result.unique().all()]

    async def get_one(self, sm_id: UUID):
        async with self.session() as session:
            try:
                result = await session.execute(get_one_submenu(sm_id))
                return result.first()._asdict()
            except (NoResultFound, AttributeError):
                return None

    async def delete_one(self, sm_id: UUID):
        stmt = delete(self.table).filter_by(id=sm_id)
        async with self.session() as session:
            try:
                await session.execute(stmt)
                await session.commit()
                return True
            except IntegrityError:
                return None

    async def update_one(self, value: dict, sm_id: UUID):
        stmt = (update(self.table).values(**value).filter_by(id=sm_id)
                .returning(self.table.c.id))
        async with self.session() as session:
            try:
                dict_id = (await session.execute(stmt)).first()._asdict()
                result = (await session.execute(get_one_submenu(dict_id['id']))).first()._asdict()
                await session.commit()
                return result
            except IntegrityError:
                return None

