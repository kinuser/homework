"""Reusable CRUD tests"""
import asyncio
from uuid import UUID

import pytest
from db_dependencies.database import Session
from db_dependencies.models import dish_table
from db_dependencies.redis_repos import DishRedisRepo
from db_dependencies.uofs import DishesUOF
from httpx import AsyncClient
from sqlalchemy import select
from utils import reverse

from tests.test_schemas import DishSchema, OutputDishSchema
from tests.test_y_menu_crud import create_menu, delete_menu
from tests.test_y_submenu_crud import create_submenu


async def create_dish(m_id: UUID, sm_id: UUID) -> OutputDishSchema | None:
    """Create dish in Database"""
    values = {
        'title': 'My dish',
        'description': 'My submenu dish',
        'price': '10.00',
        'submenu_id': sm_id
    }
    resp = await DishesUOF.create(m_id, sm_id, DishSchema(**values))
    if resp:
        return resp
    return None


async def get_cache_d(m_id: UUID, sm_id: UUID, d_id: UUID):
    """Get dish from cache"""
    resp = await DishRedisRepo.get(m_id, sm_id, d_id)
    return resp


@pytest.mark.asyncio(scope='session')
class TestYDishCrud:
    """
    Group of CRUD tests for testing dish.
    Every test are fully independent
    """
    async def test_post_dish(self):
        """Testing post"""
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.post(
                reverse('post_dish', menu.id, submenu.id),
                json={
                    'title': 'My dish',
                    'description': 'My dish description',
                    'price': '12.50'
                })
            assert r.status_code == 201
            item = OutputDishSchema(**r.json())
            assert item.title == 'My dish'
            assert item.description == 'My dish description'
        async with Session() as s:
            db_obj = OutputDishSchema(
                **(await s.execute(select(dish_table).filter_by(id=item.id)))
                .one()._asdict()
            )
            await asyncio.sleep(1)
            cache_obj = await get_cache_d(menu.id, submenu.id, item.id)
            assert item == db_obj == cache_obj
        await delete_menu(menu.id)

    async def test_get_dish(self):
        """Testing get"""
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        dish = await create_dish(menu.id, submenu.id)
        async with AsyncClient() as client:
            r = await client.get(
                reverse('get_dish', menu.id, submenu.id, dish.id)
            )
            assert r.status_code == 200
            item = OutputDishSchema(**r.json())
            cache_obj = await get_cache_d(menu.id, submenu.id, item.id)
            assert dish == item == cache_obj
        await delete_menu(menu.id)

    async def test_get_all_dish(self):
        """Testing get all"""
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        await create_dish(menu.id, submenu.id)
        await create_dish(menu.id, submenu.id)
        await create_dish(menu.id, submenu.id)
        async with Session() as s:
            result = await s.execute(
                select(dish_table)
                .filter_by(submenu_id=submenu.id)
            )
            db_obj_list = [
                OutputDishSchema(**x._asdict()) for x in result.all()
            ]
            cache_obj_list = [
                x for x in await DishRedisRepo.get_all(menu.id, submenu.id)
            ]
        async with AsyncClient() as client:
            r = await client.get(
                reverse('get_all_dishes', menu.id, submenu.id)
            )
            assert r.status_code == 200
            items_list = [OutputDishSchema(**x) for x in r.json()]
            db_obj_list = sorted(db_obj_list, key=lambda x: x.id, reverse=True)
            items_list = sorted(items_list, key=lambda x: x.id, reverse=True)
            cache_obj_list = sorted(cache_obj_list, key=lambda x: x.id, reverse=True)
            assert db_obj_list == items_list == cache_obj_list
        await delete_menu(menu.id)

    async def test_update_dish(self):
        """Testing update"""
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        dish = await create_dish(menu.id, submenu.id)
        async with AsyncClient() as client:
            r = await client.patch(
                reverse('update_dish', menu.id, submenu.id, dish.id),
                json={
                    'title': 'My updated dish',
                    'description': 'My updated dish description',
                    'price': '9.00'
                })
            assert r.status_code == 200
            item = OutputDishSchema(**r.json())
        async with Session() as s:
            db_obj = OutputDishSchema(
                **(await s.execute(
                    select(dish_table)
                    .filter_by(submenu_id=submenu.id))
                   )
                .one()._asdict()
            )
            await asyncio.sleep(1)
            cache_obj = await get_cache_d(menu.id, submenu.id, item.id)
            assert item == db_obj == cache_obj
        await delete_menu(menu.id)

    async def test_delete_dish(self):
        """Testing delete"""
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        dish = await create_dish(menu.id, submenu.id)
        async with AsyncClient() as client:
            r = await client.delete(
                reverse('delete_dish', menu.id, submenu.id, dish.id)
            )
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(select(dish_table).filter_by(id=dish.id))
            await asyncio.sleep(1)
            cache_resp = await DishRedisRepo.get(menu.id, submenu.id, dish.id)
            assert cache_resp is False
            assert result.all() == []
        await delete_menu(menu.id)
