from pydantic import BaseModel
from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from models import DishOrm
from repositories.abstract import AbstractRepository
from uuid import UUID


class DishRepository(AbstractRepository):
    orm: DishOrm

    async def create_one(self, value: dict, sm_id: UUID):
        value['submenu_id'] = sm_id
        stmt = insert(self.orm).values(**value).returning(self.orm)
        async with self.session() as session:
            try:
                result = await session.execute(stmt)
                resp = result.scalar_one().to_read_model()
                await session.commit()
                return resp
            except IntegrityError:
                return None

    async def get_all(self, sm_id: UUID):
        query = select(self.orm).filter_by(submenu_id=sm_id)
        async with self.session() as session:
            result = await session.execute(query)
            return [x.to_read_model() for x in result.scalars().unique()]

    async def get_one(self, d_id: UUID):
        query = select(self.orm).filter_by(id=d_id)
        async with self.session() as session:
            result = await session.execute(query)
            try:
                return result.scalar_one().to_read_model()
            except NoResultFound:
                return None

    async def delete_one(self, d_id: UUID):
        stmt = delete(self.orm).filter_by(id=d_id)
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_one(self, value: dict, d_id: UUID):
        stmt = update(self.orm).values(value).filter_by(id=d_id).returning(self.orm.id)
        async with self.session() as session:
            result = (await session.execute(stmt)).scalar_one()
            new_result = await session.execute(
                select(self.orm)
                .filter_by(id=result)
                .execution_options(populate_existing=True)
            )
            resp = [x.to_read_model() for x in new_result.scalars()]
            await session.commit()
            return resp[0]
