"""Classes for synchronization between Redis and SQL Database"""
from uuid import UUID

from database import Session
from repositories.dish import DishRepository
from repositories.menu import MenuRepository
from repositories.redis_repos import DishRedisRepo, MenuRedisRepo, SubmenuRedisRepo
from repositories.submenu import SubmenuRepository
from schemas import (
    DishSchema,
    MenuSchema,
    OutputDishSchema,
    OutputMenuSchema,
    OutputSubmenuSchema,
    SubmenuSchema,
)


class MenuUOF:
    """Class for menu"""
    @classmethod
    async def create(cls, menu: MenuSchema) -> OutputMenuSchema:
        """Create one object in SQL DB and cache it"""
        async with Session() as s:
            r = MenuRepository(s)
            db_r = await r.create_one(menu)
            if db_r:
                red_r = await MenuRedisRepo.create(db_r)
                if red_r:
                    await s.commit()
                    return db_r
                raise Exception('Synchronization error for menu')
            raise Exception('Error, something went wrong')

    @classmethod
    async def get_all(cls) -> list[OutputMenuSchema]:
        """Get all objects"""
        resp = await MenuRedisRepo.get_all()
        return resp

    @classmethod
    async def get(cls, m_id: UUID) -> OutputMenuSchema | None:
        """Get one object"""
        resp = await MenuRedisRepo.get(m_id)
        if resp and resp is not True:
            return resp
        return None

    @classmethod
    async def delete(cls, m_id: UUID) -> bool:
        """Delete one object in SQL DB and in Redis"""
        async with Session() as s:
            r = MenuRepository(s)
            if await r.delete_one(m_id):
                if await MenuRedisRepo.delete(m_id):
                    await s.commit()
                    return True
                print('Synchronization error from delete menu')
                return False
            return False

    @classmethod
    async def update(cls, m_id: UUID, menu: MenuSchema) -> OutputMenuSchema | None:
        """Update one object in SQL DB and cache it"""
        async with Session() as s:
            r = MenuRepository(s)
            db_r = await r.update_one(m_id, menu)
            if db_r:
                if await MenuRedisRepo.update(db_r.id, db_r):
                    await s.commit()
                    return db_r
                print('Synchronization error from update menu')
                return None
            return None


class SubmenuUOF:
    """Class for submenu"""
    @classmethod
    async def create(cls, m_id: UUID, submenu: SubmenuSchema) -> OutputSubmenuSchema | None:
        """Create one object in SQL DB and cache it"""
        async with Session() as s:
            r = SubmenuRepository(s)
            r_m = MenuRepository(s)
            db_r = await r.create_one(submenu, m_id)
            if db_r:
                if await SubmenuRedisRepo.create(m_id, db_r):
                    upd_menu = await r_m.get_one(m_id)
                    if upd_menu:
                        await MenuRedisRepo.update(m_id, upd_menu)
                        await s.commit()
                        return db_r
                raise Exception('Cache synchronization error')
            return None

    @classmethod
    async def get_all(cls, m_id: UUID) -> list[OutputSubmenuSchema]:
        """Get all objects"""
        resp = await SubmenuRedisRepo.get_all(m_id)
        return resp

    @classmethod
    async def get(cls, m_id: UUID, sm_id: UUID) -> OutputSubmenuSchema | None:
        """Get one object"""
        resp = await SubmenuRedisRepo.get(m_id, sm_id)
        if resp:
            return resp
        return None

    @classmethod
    async def delete(cls, m_id: UUID, sm_id: UUID) -> bool:
        """Delete one object in SQL DB and in Redis, and invalidate  cache"""
        async with Session() as s:
            r = SubmenuRepository(s)
            r_m = MenuRepository(s)
            await r.delete_one(sm_id)
            await SubmenuRedisRepo.delete(m_id, sm_id)
            upd_m = await r_m.get_one(m_id)
            if upd_m:
                await MenuRedisRepo.update(m_id, upd_m)
                await s.commit()
                return True
            return False

    @classmethod
    async def update(
            cls,
            m_id: UUID,
            sm_id: UUID,
            submenu: SubmenuSchema) -> OutputSubmenuSchema | None:
        """Update one object in SQL DB and cache it"""
        async with Session() as s:
            r = SubmenuRepository(s)
            db_r = await r.update_one(submenu, sm_id)
            if db_r:
                if await SubmenuRedisRepo.update(m_id, db_r.id, db_r):
                    await s.commit()
                    return db_r
                print('Synchronization error from update submenu')
                return None
            return None


class DishesUOF:
    """Class that synchronize SQL Database and Redis. F.e. invalidation"""
    @classmethod
    async def create(cls, m_id: UUID,
                     sm_id: UUID, dish: DishSchema) -> OutputDishSchema | None:
        """Create one object in SQL DB and cache it"""
        async with Session() as s:
            r = DishRepository(s)
            sm_r = SubmenuRepository(s)
            m_r = MenuRepository(s)
            db_r = await r.create_one(dish, sm_id)
            if db_r:
                if await DishRedisRepo.create(m_id, sm_id, db_r):
                    upd_m = await m_r.get_one(m_id)
                    upd_sm = await sm_r.get_one(sm_id)
                    if upd_m and upd_sm:
                        await MenuRedisRepo.update(m_id, upd_m)
                        await SubmenuRedisRepo.update(m_id, sm_id, upd_sm)
                    await s.commit()
                    return db_r
                raise Exception('Cache synchronization error')
            return None

    @classmethod
    async def get_all(cls, m_id: UUID, sm_id: UUID) -> list[OutputDishSchema]:
        """Get all objects"""
        resp = await DishRedisRepo.get_all(m_id, sm_id)
        return resp

    @classmethod
    async def get(cls, m_id: UUID, sm_id: UUID, d_id: UUID) -> OutputDishSchema | None:
        """Get one object"""
        resp = await DishRedisRepo.get(m_id, sm_id, d_id)
        if not isinstance(resp, bool):
            return resp
        return None

    @classmethod
    async def delete(cls, m_id: UUID, sm_id: UUID, d_id: UUID) -> bool:
        """Delete one object in SQL DB and in Redis"""
        async with Session() as s:
            sm_r = SubmenuRepository(s)
            m_r = MenuRepository(s)
            r = DishRepository(s)
            if await r.delete_one(d_id):
                if await DishRedisRepo.delete(m_id, sm_id, d_id):
                    upd_m = await m_r.get_one(m_id)
                    upd_sm = await sm_r.get_one(sm_id)
                    if upd_m and upd_sm:
                        await MenuRedisRepo.update(m_id, upd_m)
                        await SubmenuRedisRepo.update(m_id, sm_id, upd_sm)
                    await s.commit()
                    return True
                print('Synchronization error from delete submenu')
                return False
            return False

    @classmethod
    async def update(cls, m_id: UUID, sm_id: UUID,
                     d_id: UUID, dish: DishSchema) -> OutputDishSchema | None:
        """Update one object in SQL DB and cache it"""
        async with Session() as s:
            r = DishRepository(s)
            db_r = await r.update_one(dish, d_id)
            if db_r:
                if await DishRedisRepo.update(m_id, sm_id, db_r.id, db_r):
                    await s.commit()
                    return db_r
                print('Synchronization error from update submenu')
                return None
            return None
