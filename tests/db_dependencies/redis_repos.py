"""Module represents Redis repositories"""
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from test_config import RED_HOST, RED_PORT


def get_c():
    """Get redis client"""
    return redis.Redis(host=RED_HOST, port=RED_PORT, decode_responses=True)


class MenuRedisRepo:
    """Class represents menu repository"""

    def __init__(self, session: AsyncSession):
        self.s = session

    @classmethod
    async def get(cls, m_id: UUID) -> dict | bool:
        """Get menu from Redis cache"""
        r = get_c()
        resp = await r.json().get('menus', f'$.[?(@id=="{str(m_id)}")]')
        await r.aclose()
        if len(resp) == 1:
            del resp[0]['submenus']
            return resp[0]
        return False

    @classmethod
    async def get_all(cls) -> list[dict | None]:
        """Get all menus from Redis cache"""
        r = get_c()
        resp = (await r.json().get('menus'))
        await r.aclose()
        if len(resp) >= 1:
            for x in resp:
                del x['submenus']
        return resp

    @classmethod
    async def update(cls, m_id: UUID, values: dict) -> bool:
        """Update menu from Redis cache"""
        r = get_c()
        resp = [
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].title',
                values['title']
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].description',
                values['description']
            ),
        ]

        if 'submenus_count' in values:
            resp.extend([
                await r.json().set(
                    'menus',
                    f'$.[?(@id=="{m_id}")]["dishes_count"]',
                    values['dishes_count']
                ),
                await r.json().set(
                    'menus', f'$.[?(@id=="{m_id}")]["submenus_count"]',
                    values['submenus_count']
                )
            ])
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
    async def create(cls, values: dict) -> bool:
        """Add menu to redis cache"""
        r = get_c()
        values['submenus'] = []
        values['id'] = str(values['id'])
        await r.json().arrappend('menus', '$', values)
        del values['submenus']
        await r.aclose()
        return True


class SubmenuRedisRepo:
    """Class represents submenu repository"""
    @classmethod
    async def get(cls, m_id: UUID, sm_id: UUID):
        """Get submenu"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
        )
        await r.aclose()
        if len(resp) == 1:
            del resp[0]['dishes']
            return resp[0]
        return None

    @classmethod
    async def get_all(cls, m_id: UUID):
        """Get all submenus by id"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.*'
        )
        await r.aclose()
        if len(resp) >= 1:
            for x in resp:
                del x['dishes']
        return resp

    @classmethod
    async def update(cls, m_id: UUID, sm_id: UUID, values: dict):
        """Update submenu"""

        r = get_c()
        resp = [
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus'
                f'.[?(@id=="{str(sm_id)}")].title',
                values['title']
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus'
                f'.[?(@id=="{str(sm_id)}")].description',
                values['description']
            )
        ]
        if 'dishes_count' in values:
            resp.extend([await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus'
                f'.[?(@id=="{str(sm_id)}")]["dishes_count"]',
                values['dishes_count'])]
            )
        await r.aclose()
        if all(x for x in resp if x):
            return True
        return False

    @classmethod
    async def delete(cls, m_id, sm_id):
        """Delete submenu"""
        r = get_c()
        resp = await r.json().delete(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
        )
        await r.aclose()
        if resp == 1:
            return True

    @classmethod
    async def create(cls, m_id: UUID, values: dict):
        """Create submenu"""
        r = get_c()
        values['dishes'] = []
        values['id'] = str(values['id'])
        del values['menu_id']
        await r.json().arrappend(
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
    async def get(cls, m_id: UUID, sm_id: UUID, d_id: UUID):
        """Get dish"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
            f'.dishes.[?(@id=="{str(d_id)}")]'
        )
        await r.aclose()
        if len(resp) == 1:
            return resp[0]
        return False

    @classmethod
    async def get_all(cls, m_id: UUID, sm_id: UUID):
        """Get all dish by submenu id"""
        r = get_c()
        resp = await r.json().get(
            'menus',
            f'$.[?(@id=="{str(m_id)}")]'
            f'.submenus.[?(@id=="{str(sm_id)}")].dishes.*'
        )
        await r.aclose()
        return resp

    @classmethod
    async def update(cls, m_id: UUID, sm_id: UUID, d_id: UUID, values: dict):
        """Update dish"""
        r = get_c()
        resp = [
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
                f'.dishes.[?(@id=="{str(d_id)}")].title',
                values['title']
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
                f'.dishes.[?(@id=="{str(d_id)}")].description',
                values['description']
            ),
            await r.json().set(
                'menus',
                f'$.[?(@id=="{str(m_id)}")].submenus.[?(@id=="{str(sm_id)}")]'
                f'.dishes.[?(@id=="{str(d_id)}")].price',
                values['price'])
        ]
        await r.aclose()
        if all(x for x in resp if x):
            return True

    @classmethod
    async def delete(cls, m_id: UUID, sm_id: UUID, d_id: UUID):
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

    @classmethod
    async def create(cls, m_id: UUID, sm_id: UUID, values: dict):
        """Create dish"""
        r = get_c()
        values['id'] = str(values['id'])
        del values['submenu_id']
        await r.json().arrappend(
            'menus',
            f'$.[?(@id=="{str(m_id)}")].submenus'
            f'.[?(@id=="{str(sm_id)}")].dishes',
            values
        )
        await r.aclose()
        return True
