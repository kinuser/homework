from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update, func, exists
from sqlalchemy.exc import NoResultFound, IntegrityError
from models import submenu_table, dish_table, menu_table, get_one_menu
from repositories.abstract import AbstractRepository
from uuid import UUID
from models import get_all_menus




class MenuRepository(AbstractRepository):

    async def create_one(self, value: dict):
        stmt = insert(self.table).values(**value).returning(self.table.c.id)
        async with self.session() as session:
            dict_id = (await session.execute(stmt)).first()._asdict()
            result = (await session.execute(get_one_menu(dict_id['id']))).first()._asdict()
            await session.commit()
            return result

    async def get_all(self):
        query = get_all_menus()
        print(query.compile(compile_kwargs={"literal_binds": True}))
        async with self.session() as session:
            result = await session.execute(query)
            return [x._asdict() for x in result.all()]

    async def get_one(self, id: UUID):
        query = get_one_menu(id)
        async with self.session() as session:
            try:
                result = await session.execute(query)
                return result.one()._asdict()
            except (NoResultFound, AttributeError):
                return None

    async def delete_one(self, id: UUID):
        stmt = delete(self.table).filter_by(id=id)
        async with self.session() as session:
            try:
                await session.execute(stmt)
                await session.commit()
                return True
            except IntegrityError:
                return None

    async def update_one(self, value: dict, id: UUID):
        stmt = (update(self.table)
                .values(**value)
                .where(self.table.c.id == id)
                .returning(self.table.c.id))
        async with self.session() as session:
            try:
                dict_id = (await session.execute(stmt)).first()._asdict()
                result = (await session.execute(get_one_menu(dict_id['id']))).first()._asdict()
                await session.commit()
                return result
            except (IntegrityError, AttributeError):
                return None
