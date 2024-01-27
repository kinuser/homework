from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import NoResultFound, IntegrityError
from models import MenuOrm
from repositories.abstract import AbstractRepository
from uuid import UUID


class MenuRepository(AbstractRepository):
    orm: MenuOrm

    async def create_one(self, item: dict):
        stmt = insert(self.orm).values(item).returning(self.orm.id)
        async with self.session() as session:
            result = (await session.execute(stmt)).scalar_one()
            response = await session.execute(
                select(self.orm)
                .filter_by(id=result)
            )
            response = response.unique().scalar_one().to_read_model()
            await session.commit()
            return self.to_repr_one(response)

    async def get_all(self) -> list:
        query = select(self.orm)
        async with self.session() as session:
            result = await session.execute(query)
            return self.to_repr_all([x.to_read_model() for x in result.unique().scalars().all()])

    async def get_one(self, id: UUID):
        query = select(self.orm).filter_by(id=id)
        async with self.session() as session:
            try:
                result = (await session.execute(query)).unique().scalar_one().to_read_model()
                return self.to_repr_one(result)
            except NoResultFound:
                return None

    async def delete_one(self, id: UUID):
        stmt = delete(self.orm).filter_by(id=id)
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_one(self, value: dict, id: UUID):
        stmt = update(self.orm).values(value).filter_by(id=id).returning(self.orm.id)
        async with self.session() as session:
            try:
                result = (await session.execute(stmt)).scalar_one()
                response = await session.execute(
                    select(self.orm)
                    .filter_by(id=result)
                )
                response = response.unique().scalar_one().to_read_model()
                await session.commit()
                return self.to_repr_one(response)
            except IntegrityError:
                return None


    def to_repr_all(self, arg: list):
        for menu in arg:
            self.to_repr_one(menu)
        return arg

    def to_repr_one(self, arg: dict):
        arg['submenus_count'] = len(arg['submenu'])
        dishes = 0
        for x in arg['submenu']:
            dishes = len(x['dish']) + dishes
        arg['dishes_count'] = dishes
        del arg['submenu']
        return arg
