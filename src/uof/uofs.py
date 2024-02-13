"""Classes for synchronization between Redis and SQL Database"""
from uuid import UUID

from sqlalchemy import select

from database import Session
from models import dish_table
from my_celery.schemas import DishSchemaTable, MenuSchemaTable, SubmenuSchemaTable
from repositories.dish import DishRepository
from repositories.menu import MenuRepository, get_all_menus
from repositories.redis_repos import DishRedisRepo, MenuRedisRepo, SubmenuRedisRepo
from repositories.submenu import SubmenuRepository, get_every_submenu
from schemas import (
    DishSchema,
    MenuSchema,
    MenuSchemaAll,
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


class AllUOF:
    """Class represents actions between al entities of db"""
    @classmethod
    async def synchronize_gsheet(
            cls,
            menu_list: list[MenuSchemaTable],
            submenu_list: list[SubmenuSchemaTable],
            dish_list: list[DishSchemaTable],
    ):
        """Synchronize all SQLDatabase with external values"""
        async with Session() as s:
            menu_r = MenuRepository(s)
            submenu_r = SubmenuRepository(s)
            dish_r = DishRepository(s)
            await menu_r.synchronize(menu_list)
            await submenu_r.synchronize(submenu_list)
            await dish_r.synchronize(dish_list)
            await s.commit()

    @classmethod
    async def get_everything(cls) -> list[MenuSchemaAll]:
        """Get everything from database with complex ORM query"""
        menu_cte = get_all_menus().cte()
        submenu_cte = get_every_submenu().cte()
        query = (
            select(
                menu_cte,
                submenu_cte,
                dish_table
            )
            .outerjoin_from(menu_cte, submenu_cte, menu_cte.c.id == submenu_cte.c.menu_id)
            .outerjoin_from(submenu_cte, dish_table, submenu_cte.c.id == dish_table.c.submenu_id)
        )
        async with Session() as s:
            res = (await s.execute(query)).all()
            if not res:
                return []
            all_list = [x._asdict() for x in res]
            menu_list = []
            # Find all menus
            for i in all_list:
                menu: dict = {}
                for key, value in i.items():
                    if key in ('title', 'description', 'id', 'dishes_count', 'submenus_count'):
                        menu[key] = value
                menu_list.append(menu)
            menu_list = [dict(t) for t in {tuple(d.items()) for d in menu_list}]
            # Find all submenus
            submenu_list = []
            for i in all_list:
                submenu: dict = {}
                for key, value in i.items():
                    if key in ('title_1', 'description_1', 'id_1', 'menu_id', 'dishes_count'):
                        submenu[key] = value
                submenu_list.append(submenu)
            submenu_list = [dict(t) for t in {tuple(d.items()) for d in submenu_list}]
            # Find all dishes
            dishes_list = []
            for i in all_list:
                dish: dict = {}
                for key, value in i.items():
                    if key in ('title_2', 'description_2', 'id_2', 'submenu_id', 'price'):
                        dish[key] = value
                dishes_list.append(dish)
            # Unite three lists
            for submenu in submenu_list:
                submenu['dishes'] = []
                submenu['id'] = submenu['id_1']
                submenu['title'] = submenu['title_1']
                submenu['description'] = submenu['description_1']
                del submenu['id_1']
                del submenu['title_1']
                del submenu['description_1']
            for dish in dishes_list:
                dish['id'] = dish['id_2']
                dish['title'] = dish['title_2']
                dish['description'] = dish['description_2']
                del dish['id_2']
                del dish['title_2']
                del dish['description_2']
            for menu in menu_list:
                menu['submenus'] = []
            for dish in dishes_list:
                for submenu in submenu_list:
                    if dish['submenu_id'] == submenu['id']:
                        submenu['dishes'].append(dish)
            for submenu in submenu_list:
                for menu in menu_list:
                    if submenu['menu_id'] == menu['id']:
                        menu['submenus'].append(submenu)

            return [MenuSchemaAll(**x) for x in menu_list]
