"""Module contains dish repository"""

from uuid import UUID

from db_dependencies.models import dish_table
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


# noinspection PyProtectedMember
class DishRepository:
    """Dish repository for SQL DB"""

    def __init__(self, session: AsyncSession):
        self.s = session

    async def create_one(
            self, value: dict,
            sm_id: UUID) -> dict | None:
        """Create one dish record"""
        value['submenu_id'] = sm_id
        stmt = insert(dish_table).values(**value).returning(dish_table)
        try:
            result = await self.s.execute(stmt)
            await self.s.commit()
            return result.first()._asdict()
        except IntegrityError:
            return None

    async def get_all(self, sm_id: UUID) -> list[dict]:
        """Get all dishes"""
        query = select(dish_table).where(dish_table.c.submenu_id == sm_id)
        result = await self.s.execute(query)
        return [x._asdict() for x in result.all()]

    async def get_one(self, d_id: UUID) -> dict | None:
        """Get one dish"""
        query = select(dish_table).filter_by(id=d_id)
        try:
            result = await self.s.execute(query)
            return result.first()._asdict()
        except (NoResultFound, AttributeError):
            return None

    async def delete_one(self, d_id: UUID) -> bool | None:
        """Delete one dish"""
        stmt = delete(dish_table).where(dish_table.c.id == d_id)
        try:
            await self.s.execute(stmt)
            await self.s.commit()
            return True
        except IntegrityError:
            return None

    async def update_one(self, value: dict, d_id: UUID) -> dict | None:
        """Update one dish"""
        stmt = (update(dish_table).values(**value)
                .where(dish_table.c.id == d_id)
                .returning(dish_table)
                )
        result = await self.s.execute(stmt)
        await self.s.commit()
        try:
            return result.first()._asdict()
        except IntegrityError:
            return None
