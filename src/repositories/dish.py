"""Module contains dish repository"""

from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from models import dish_table
from my_celery.schemas import DishSchemaTable
from schemas import DishSchema, OutputDishSchema


# noinspection PyProtectedMember
class DishRepository:
    """Dish repository for SQL DB"""

    def __init__(self, session: AsyncSession):
        self.s = session

    async def create_one(
            self, dish: DishSchema,
            sm_id: UUID) -> OutputDishSchema | None:
        """Create one dish record"""
        dish = dish.model_dump()
        dish['submenu_id'] = sm_id
        stmt = insert(dish_table).values(**dish).returning(dish_table)
        try:
            result = await self.s.execute(stmt)
            return OutputDishSchema(**result.first()._asdict())
        except IntegrityError:
            return None

    async def get_all(self, sm_id: UUID) -> list[OutputDishSchema]:
        """Get all dishes"""
        query = select(dish_table).where(dish_table.c.submenu_id == sm_id)
        result = (await self.s.execute(query)).all()
        if len(result) > 0:
            return [OutputDishSchema(**x._asdict()) for x in result]
        return []

    async def get_one(self, d_id: UUID) -> OutputDishSchema | None:
        """Get one dish"""
        query = select(dish_table).filter_by(id=d_id)
        try:
            result = await self.s.execute(query)
            return OutputDishSchema(**result.first()._asdict())
        except (NoResultFound, AttributeError):
            return None

    async def delete_one(self, d_id: UUID) -> bool | None:
        """Delete one dish"""
        stmt = delete(dish_table).where(dish_table.c.id == d_id)
        try:
            await self.s.execute(stmt)
            return True
        except IntegrityError:
            return None

    async def update_one(self, dish: DishSchema, d_id: UUID) -> OutputDishSchema | None:
        """Update one dish"""
        stmt = (update(dish_table).values(**dish.model_dump())
                .where(dish_table.c.id == d_id)
                .returning(dish_table)
                )
        result = await self.s.execute(stmt)
        try:
            return OutputDishSchema(**result.first()._asdict())
        except IntegrityError:
            return None

    async def get_everything(self):
        """Get all table"""
        query = select(dish_table)
        result = (await self.s.execute(query)).all()
        if len(result) > 0:
            return [OutputDishSchema(**x._asdict()) for x in result]
        return []

    async def synchronize(self, menu_list: list[DishSchemaTable]) -> bool:
        """Synchronize SQL table with """
        current_state = await self.get_everything()
        # Check for delete
        for x in current_state:
            answer = False
            for n in menu_list:
                if x.id == n.id:
                    answer = True
            if answer is False:
                await self.delete_one(x.id)
        # Insert or update
        stmt = (
            insert(dish_table)
            .values([x.model_dump() for x in menu_list])
        )
        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_={
                'title': stmt.excluded.title,
                'description': stmt.excluded.description
            }
        )
        await self.s.execute(do_update_stmt)

        return True
