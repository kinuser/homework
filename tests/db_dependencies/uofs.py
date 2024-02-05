"""Classes for synchronization between Redis and SQL Database"""
from uuid import UUID

from db_dependencies.database import Session
from db_dependencies.dish import DishRepository
from db_dependencies.menu import MenuRepository
from db_dependencies.redis_repos import DishRedisRepo, MenuRedisRepo, SubmenuRedisRepo
from db_dependencies.submenu import SubmenuRepository


class MenuUOF:
    """Class for menu"""
    @classmethod
    async def create(cls, values: dict) -> dict | None:
        """Create one object in SQL DB and cache it"""
        async with Session() as s:
            r = MenuRepository(s)
            db_r = await r.create_one(values)
            if db_r:
                red_r = await MenuRedisRepo.create(db_r)
                if red_r:
                    await s.commit()
                    return db_r
                error = 'Synchronization error from create menu'
                print(error)
                return {'error': error}
            return None

    @classmethod
    async def get_all(cls) -> list:
        """Get all objects"""
        resp = await MenuRedisRepo.get_all()
        return resp

    @classmethod
    async def get(cls, m_id: UUID) -> dict | None:
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
    async def update(cls, m_id: UUID, values: dict) -> dict | None:
        """Update one object in SQL DB and cache it"""
        async with Session() as s:
            r = MenuRepository(s)
            db_r = await r.update_one(m_id, values)
            print(db_r)
            if db_r:
                if await MenuRedisRepo.update(db_r['id'], db_r):
                    await s.commit()
                    return db_r
                print('Synchronization error from update menu')
                return None
            return None


class SubmenuUOF:
    """Class for submenu"""
    @classmethod
    async def create(cls, m_id: UUID, values: dict) -> dict | None:
        """Create one object in SQL DB and cache it"""
        async with Session() as s:
            r = SubmenuRepository(s)
            r_m = MenuRepository(s)
            db_r = await r.create_one(values, m_id)
            if db_r:
                if await SubmenuRedisRepo.create(m_id, db_r):
                    upd_menu = await r_m.get_one(m_id)
                    if upd_menu:
                        await MenuRedisRepo.update(m_id, upd_menu)
                        await s.commit()
                        return db_r
                error = 'Synchronization error from create submenu'
                print(error)
                return {'error': error}
            return None

    @classmethod
    async def get_all(cls, m_id: UUID) -> list:
        """Get all objects"""
        resp = await SubmenuRedisRepo.get_all(m_id)
        return resp

    @classmethod
    async def get(cls, m_id: UUID, sm_id: UUID) -> dict | None:
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
                return True
            return False

    @classmethod
    async def update(
            cls,
            m_id: UUID,
            sm_id: UUID,
            values: dict) -> dict | None:
        """Update one object in SQL DB and cache it"""
        async with Session() as s:
            r = SubmenuRepository(s)
            db_r = await r.update_one(values, sm_id)
            if db_r:
                if await SubmenuRedisRepo.update(m_id, db_r['id'], db_r):
                    await s.commit()
                    return db_r
                print('Synchronization error from update submenu')
                return None
            return None


class DishesUOF:
    """Class that synchronize SQL Database and Redis. F.e. invalidation"""
    @classmethod
    async def create(cls, m_id: UUID,
                     sm_id: UUID, values: dict) -> dict | None:
        """Create one object in SQL DB and cache it"""
        async with Session() as s:
            r = DishRepository(s)
            sm_r = SubmenuRepository(s)
            m_r = MenuRepository(s)
            db_r = await r.create_one(values, sm_id)
            print('response dish sql', db_r)
            if db_r:
                if await DishRedisRepo.create(m_id, sm_id, db_r):
                    upd_m = await m_r.get_one(m_id)
                    upd_sm = await sm_r.get_one(sm_id)
                    if upd_m and upd_sm:
                        await MenuRedisRepo.update(m_id, upd_m)
                        await SubmenuRedisRepo.update(m_id, sm_id, upd_sm)
                    await s.commit()
                    return db_r
                error = 'Synchronization error from create submenu'
                print(error)
                return {'error': error}
            return None

    @classmethod
    async def get_all(cls, m_id: UUID, sm_id: UUID) -> list:
        """Get all objects"""
        resp = await DishRedisRepo.get_all(m_id, sm_id)
        return resp

    @classmethod
    async def get(cls, m_id: UUID, sm_id: UUID, d_id: UUID) -> dict | None:
        """Get one object"""
        resp = await DishRedisRepo.get(m_id, sm_id, d_id)
        if resp:
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
                     d_id: UUID, values: dict) -> dict | None:
        """Update one object in SQL DB and cache it"""
        async with Session() as s:
            r = DishRepository(s)
            db_r = await r.update_one(values, d_id)
            if db_r:
                if await DishRedisRepo.update(m_id, sm_id, db_r['id'], db_r):
                    await s.commit()
                    return db_r
                print('Synchronization error from update submenu')
                return None
            return None
