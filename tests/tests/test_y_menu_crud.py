"""Reusable CRUD tests"""
from uuid import UUID

import pytest
from db_dependencies.database import Session
from db_dependencies.menu import MenuRepository, get_all_menus
from db_dependencies.redis_repos import MenuRedisRepo
from db_dependencies.uofs import MenuUOF
from httpx import AsyncClient
from utils import reverse

from tests.test_schemas import OutputMenuSchema


async def create_menu() -> OutputMenuSchema | None:
    """Create menu in DB and cache"""
    resp = await MenuUOF.create({
        'title': 'My menu 1',
        'description': 'My menu description 1'
    })
    if resp:
        return OutputMenuSchema(**resp)
    return None


async def delete_menu(m_id: UUID) -> None:
    """Create menu in DB and cache"""
    await MenuUOF.delete(m_id)


async def get_cmenu(m_id: UUID) -> dict | None:
    """Get menu from cache"""
    resp = await MenuRedisRepo.get(m_id)
    if isinstance(resp, dict):
        return resp
    return None


@pytest.mark.asyncio(scope='session')
class TestYMenuCrud:
    """
    Group of CRUD tests for testing menu.
    Every test are fully independent
    """
    async def test_post_menu(self):
        """Testing post"""
        async with AsyncClient() as client:
            r = await client.post(reverse('menu'), json={
                'title': 'My menu 1',
                'description': 'My menu description 1'
            })
            assert r.status_code == 201
            item = OutputMenuSchema(**r.json())
            assert item.title == 'My menu 1'
            assert item.description == 'My menu description 1'
            async with Session() as s:
                db_item = OutputMenuSchema(**await MenuRepository(s).get_one(item.id))
                cache_item = OutputMenuSchema(**await get_cmenu(item.id))
                assert item == db_item == cache_item
            await delete_menu(item.id)

    async def test_get_menu(self):
        """Testing get"""
        db_menu = await create_menu()
        async with AsyncClient() as client:
            r = await client.get(reverse('menu', db_menu.id))
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
        assert db_menu == item
        await delete_menu(db_menu.id)

    async def test_get_all_menus(self):
        """Testing get all"""
        menu_1 = await create_menu()
        menu_2 = await create_menu()
        async with Session() as s:
            result = await s.execute(get_all_menus())
            db_obj_list = [OutputMenuSchema(**x._asdict()) for x in result.all()]
            cache_obj_list = [OutputMenuSchema(**x) for x in await MenuRedisRepo.get_all()]
            async with AsyncClient() as client:
                r = await client.get(reverse('menu'))
                assert r.status_code == 200
                items_list = [OutputMenuSchema(**x) for x in r.json()]
                db_obj_list = sorted(db_obj_list, key=lambda x: x.id, reverse=True)
                items_list = sorted(items_list, key=lambda x: x.id, reverse=True)
                cache_obj_list = sorted(cache_obj_list, key=lambda x: x.id, reverse=True)
                assert db_obj_list == items_list == cache_obj_list
        await delete_menu(menu_1.id)
        await delete_menu(menu_2.id)

    async def test_update_menu(self):
        """Testing update"""
        menu = await create_menu()
        values = {
            'title': 'Updated menu title',
            'description': 'Updated menu description'
        }
        async with AsyncClient() as client:
            r = await client.patch(
                reverse('menu', menu.id),
                json=values
            )
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert item.title == values['title']
            assert item.description == values['description']
            updated_db_menu = OutputMenuSchema(**await MenuUOF.get(menu.id))
            updated_cache_menu = OutputMenuSchema(**await MenuRedisRepo.get(menu.id))
            assert updated_db_menu == item == updated_cache_menu
        await delete_menu(updated_db_menu.id)

    async def test_delete_menu(self):
        """Testing delete"""
        db_menu = await create_menu()
        async with AsyncClient() as client:
            r = await client.delete(reverse('menu', db_menu.id))
            assert r.status_code == 200
        result = await MenuUOF.get(db_menu.id)
        assert result is None
