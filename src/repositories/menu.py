from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from models import MenuOrm, SubmenuOrm
from repositories.abstract import AbstractRepository
from uuid import UUID


class MenuRepository(AbstractRepository):
    orm: MenuOrm

    async def create_one(self, value: BaseModel):
        stmt = insert(self.orm).values(value.model_dump()).returning(self.orm.id)
        async with self.session() as session:
            result = (await session.execute(stmt)).scalar_one()
            response = await session.execute(
                select(self.orm)
                .filter_by(id=result)
                .options(selectinload(self.orm.submenu).selectinload(SubmenuOrm.dish))
                .execution_options(populate_existing=True)
            )
            response = response.scalar_one().to_read_model()
            await session.commit()
            return response

    async def get_all(self):
        query = select(self.orm)
        async with self.session() as session:
            result = await session.execute(query)
            return [x.to_read_model() for x in result.scalars().all()]

    async def get_one(self, id: UUID):
        query = select(self.orm).filter_by(id=id)
        async with self.session() as session:
            result = await session.execute(query)
            try:
                return result.scalar_one().to_read_model()
            except NoResultFound:
                return False

    async def delete_one(self, id: UUID):
        stmt = delete(self.orm).filter_by(id=id)
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_one(self, value: BaseModel, id: UUID):
        stmt = update(self.orm).values(value.model_dump()).filter_by(id=id).returning(self.orm.id)
        async with self.session() as session:
            result = (await session.execute(stmt)).scalar_one()
            response = await session.execute(
                select(self.orm)
                .filter_by(id=result)
                .options(selectinload(self.orm.submenu).selectinload(SubmenuOrm.dish))
                .execution_options(populate_existing=True)
            )
            response = response.scalar_one().to_read_model()
            await session.commit()
            return response

    def to_repr_all(self, arg: dict):
        for menu in arg:
            menu['submenus_count'] = len(menu['submenu'])
            dishes = 0
            for x in menu['submenu']:
                dishes = len(x['dish']) + dishes
            menu['dishes_count'] = dishes
            del menu['submenu']
        return arg

    def to_repr_one(self, arg: dict):
        arg['submenus_count'] = len(arg['submenu'])
        dishes = 0
        for x in arg['submenu']:
            dishes = len(x['dish']) + dishes
        arg['dishes_count'] = dishes
        del arg['submenu']
        return arg
