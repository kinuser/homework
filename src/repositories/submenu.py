from sqlalchemy import insert, select, delete, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import selectinload
from models import SubmenuOrm
from repositories.abstract import AbstractRepository
from uuid import UUID


class SubmenuRepository(AbstractRepository):
    orm: SubmenuOrm

    async def create_one(self, value: dict, m_id: UUID):
        value['menu_id'] = m_id
        stmt = insert(self.orm).values(**value).returning(self.orm.id)
        async with self.session() as session:
            try:
                result = (await session.execute(stmt)).scalar_one()
                response = await session.execute(
                    select(self.orm)
                    .filter_by(id=result)
                    .execution_options(populate_existing=True)
                )
                response = response.unique().scalar_one().to_read_model()
                await session.commit()
                return self.to_repr_one(response)
            except IntegrityError:
                return None

    async def get_all(self, m_id: UUID):
        query = select(self.orm).filter_by(menu_id=m_id)
        async with self.session() as session:
            result = await session.execute(query)
            return self.to_repr_all([x.to_read_model() for x in result.unique().scalars().all()])

    async def get_one(self, sm_id: UUID):
        query = select(self.orm).filter_by(id=sm_id).options(selectinload(self.orm.dish))
        async with self.session() as session:
            try:
                result = (await session.execute(query)).unique().scalar_one().to_read_model()
                return self.to_repr_one(result)
            except NoResultFound:
                return None

    async def delete_one(self, sm_id: UUID):
        stmt = delete(self.orm).filter_by(id=sm_id)
        async with self.session() as session:
            await session.execute(stmt)
            await session.commit()

    async def update_one(self, value: dict, sm_id: UUID):
        stmt = update(self.orm).values(value).filter_by(id=sm_id).returning(self.orm.id)
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
        for x in arg:
            self.to_repr_one(x)
        return arg

    def to_repr_one(self, arg: dict):
        arg['dishes_count'] = len(arg['dish'])
        del arg['dish']
        return arg