"""Module represents Redis repositories"""
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from test_config import RED_HOST, RED_PORT

from tests.test_schemas import OutputDishSchema, OutputMenuSchema, OutputSubmenuSchema


def get_c():
    """Get redis client"""
    if RED_HOST and RED_PORT:
        return redis.Redis(host=RED_HOST, port=int(RED_PORT), decode_responses=True)
    raise Exception("Redis env's not found")


class MenuRedisRepo:
    """Class represents menu repository"""

    def __init__(self, session: AsyncSession):
        self.s = session

    @classmethod
    async def get(cls, m_id: UUID) -> OutputMenuSchema | bool:
        """Get menu from Redis cache"""
        r = get_c()
        resp = await r.json().get('menus', f'$.[?(@id=="{str(m_id)}")]')
        await r.aclose()
        if len(resp) == 1:
            del resp[0]['submenus']
            return OutputMenuSchema(**resp[0])
        return False

    @classmethod
    async def get_all(cls) -> list[OutputMenuSchema]:
        """Get all menus from Redis cache"""
        r = get_c()
        resp = (await r.json().get('menus'))
        await r.aclose()
        if len(resp) > 0:
            for x in range(len(resp)):
                del resp[x]['submenus']
                resp[x] = OutputMenuSchema(**resp[x])
            return resp
        return []

    @classmethod
    async def update(cls, m_id: UUID, menu: OutputMenuSchema) -> bool:
        """Update menu from Redis cache"""
        r = get_c()
        resp = [
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].title',
                menu.title
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].description',
                menu.description
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{m_id}")]["dishes_count"]',
                menu.dishes_count
            ),
            await r.json().set(
                'menus', f'$.[?(@id=="{m_id}")]["submenus_count"]',
                menu.submenus_count
            )
        ]

        await r.aclose()
        gen = (x is not None for x in resp if x)
        if all(gen):
            return True
        return False

    @classmethod
    async def delete(cls, sm_id) -> bool:
        """Delete menu from Redis cache"""
        r = get_c()
        resp = await r.json().delete('menus', f'$.[?(@id=="{str(sm_id)}")]')
        await r.aclose()
        if resp == 1:
            return True
        return False

    @classmethod
    async def create(cls, menu: OutputMenuSchema) -> bool:
        """Add menu to redis cache"""
        r = get_c()
        menu = menu.model_dump()
        menu['submenus'] = []
        menu['id'] = str(menu['id'])
        await r.json().arrappend('menus', '$', menu)  # type: ignore
        await r.aclose()
        return True


class SubmenuRedisRepo:
    """Class represents submenu repository"""
    @classmethod
    async def get(cls, m_id: UUID, sm_id: UUID) -> OutputSubmenuSchema | None:
        """Get submenu"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
        )
        await r.aclose()
        if len(resp) == 1:
            del resp[0]['dishes']
            return OutputSubmenuSchema(**resp[0])
        return None

    @classmethod
    async def get_all(cls, m_id: UUID) -> list:
        """Get all submenus by id"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.*'
        )
        await r.aclose()
        if len(resp) >= 1:
            for x in range(len(resp)):
                del resp[x]['dishes']
                resp[x] = OutputSubmenuSchema(**resp[x])
            return resp
        return []

    @classmethod
    async def update(cls, m_id: UUID, sm_id: UUID, submenu: OutputSubmenuSchema) -> bool:
        """Update submenu"""

        r = get_c()
        resp = [
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus'
                f'.[?(@id=="{str(sm_id)}")].title',
                submenu.title
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus'
                f'.[?(@id=="{str(sm_id)}")].description',
                submenu.description
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus'
                f'.[?(@id=="{str(sm_id)}")]["dishes_count"]',
                submenu.dishes_count
            )
        ]
        await r.aclose()
        if all(x for x in resp if x):
            return True
        return False

    @classmethod
    async def delete(cls, m_id, sm_id) -> bool:
        """Delete submenu"""
        r = get_c()
        resp = await r.json().delete(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
        )
        await r.aclose()
        if resp == 1:
            return True
        return False

    @classmethod
    async def create(cls, m_id: UUID, submenu: OutputSubmenuSchema) -> bool:
        """Create submenu"""
        r = get_c()
        values = submenu.model_dump()
        values['dishes'] = []
        values['id'] = str(values['id'])
        values['menu_id'] = str(values['menu_id'])
        await r.json().arrappend(  # type: ignore
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus',
            values
        )
        await r.aclose()
        del values['dishes']
        return True


class DishRedisRepo:
    """Class represents dish repository for managing Redis cache"""
    @classmethod
    async def get(cls, m_id: UUID, sm_id: UUID, d_id: UUID) -> OutputDishSchema | bool:
        """Get dish"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
            f'.dishes.[?(@id=="{str(d_id)}")]'
        )
        await r.aclose()
        if len(resp) == 1:
            return OutputDishSchema(**resp[0])
        return False

    @classmethod
    async def get_all(cls, m_id: UUID, sm_id: UUID) -> list[OutputDishSchema]:
        """Get all dish by submenu id"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")]'
            f'.submenus.[?(@id=="{str(sm_id)}")].dishes.*'
        )
        await r.aclose()
        if len(resp) > 0:
            return [OutputDishSchema(**x) for x in resp]
        return []

    @classmethod
    async def update(cls, m_id: UUID, sm_id: UUID, d_id: UUID, dish: OutputDishSchema) -> bool:
        """Update dish"""
        r = get_c()
        resp = [
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
                f'.dishes.[?(@id=="{str(d_id)}")].title',
                dish.title
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
                f'.dishes.[?(@id=="{str(d_id)}")].description',
                dish.description
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
                f'.dishes.[?(@id=="{str(d_id)}")].price',
                dish.price)
        ]
        await r.aclose()
        if all(x for x in resp if x):
            return True
        return False

    @classmethod
    async def delete(cls, m_id: UUID, sm_id: UUID, d_id: UUID) -> bool:
        """Delete dish"""

        r = get_c()
        resp = await r.json().delete(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
            f'.dishes.[?(@id=="{str(d_id)}")]'
        )
        await r.aclose()
        if resp == 1:
            return True
        return False

    @classmethod
    async def create(cls, m_id: UUID, sm_id: UUID, dish: OutputDishSchema) -> bool:
        """Create dish"""
        r = get_c()
        values = dish.model_dump()
        values['id'] = str(values['id'])
        values['submenu_id'] = str(values['submenu_id'])
        await r.json().arrappend(  # type: ignore
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus'
            f'.[?(@id=="{str(sm_id)}")].dishes',
            values
        )
        await r.aclose()
        return True
