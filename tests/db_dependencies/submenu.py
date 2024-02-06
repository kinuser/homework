"""Module contains submenu repository"""
from uuid import UUID

from db_dependencies.models import dish_table, submenu_table
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from tests.test_schemas import OutputSubmenuSchema, SubmenuSchema


def get_all_submenu(sm_id: UUID) -> Select:
    """
    Get complex ORM statement for getting
    all submenus with all child counters
    """
    query = (
        select(
            submenu_table,
            func.count(dish_table.c.id).label('dishes_count')
        )
        .where(submenu_table.c.menu_id == sm_id)
        .outerjoin(
            dish_table,
            dish_table.c.submenu_id == submenu_table.c.id
        )
        .group_by(submenu_table.c.id)
    )
    return query


def get_one_submenu(sm_id: UUID):
    """
    Get complex ORM statement for getting
    one submenu with all child counters
    """
    query = (
        select(
            submenu_table,
            func.count(dish_table.c.id).label('dishes_count')
        )
        .where(submenu_table.c.id == sm_id)
        .outerjoin(dish_table, dish_table.c.submenu_id == submenu_table.c.id)
        .group_by(submenu_table.c.id)
    )
    return query


class SubmenuRepository:
    """Submenu repository for SQL DB"""

    def __init__(self, session: AsyncSession):
        self.s = session

    async def create_one(self, submenu: SubmenuSchema, m_id: UUID) -> OutputSubmenuSchema | None:
        """Get one submenu"""
        submenu = submenu.model_dump()
        submenu['menu_id'] = m_id
        stmt = (
            insert(submenu_table)
            .values(**submenu)
            .returning(submenu_table.c.id)
        )
        try:
            dict_id = (await self.s.execute(stmt)).first()._asdict()
            result = (
                (await self.s.execute(get_one_submenu(dict_id['id'])))
                .first()
                ._asdict()
            )
            return OutputSubmenuSchema(**result)
        except IntegrityError:
            return None

    async def get_all(self, m_id: UUID) -> list[OutputSubmenuSchema] | None:
        """Get all submenus"""
        result = (await self.s.execute(get_all_submenu(m_id))).unique().all()
        if len(result) > 0:
            return [OutputSubmenuSchema(**x._asdict()) for x in result]
        return []

    async def get_one(self, sm_id: UUID) -> OutputSubmenuSchema | None:
        """Get one submenu"""
        try:
            result = await self.s.execute(get_one_submenu(sm_id))
            return OutputSubmenuSchema(**result.first()._asdict())
        except (NoResultFound, AttributeError):
            return None

    async def delete_one(self, sm_id: UUID) -> bool | None:
        """Delete one submenu"""
        stmt = delete(submenu_table).filter_by(id=sm_id)
        try:
            await self.s.execute(stmt)
            return True
        except IntegrityError:
            return None

    async def update_one(self, value: SubmenuSchema, sm_id: UUID) -> OutputSubmenuSchema | None:
        """Update one submenu"""
        stmt = (update(submenu_table).values(**value.model_dump()).filter_by(id=sm_id)
                .returning(submenu_table.c.id))
        try:
            dict_id = (await self.s.execute(stmt)).first()._asdict()
            result = ((
                await self.s.execute(get_one_submenu(dict_id['id'])))
                .first()
                ._asdict()
            )
            return OutputSubmenuSchema(**result)
        except IntegrityError:
            return None
