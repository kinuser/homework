from uuid import UUID
from httpx import AsyncClient
from sqlalchemy import select, insert
from schemas import OutputDishSchema
from config import APP_HOST, APP_PORT
from models import dish_table
from database import Session
import pytest
from test_y_menu_crud import create_menu, delete_menu
from test_y_submenu_crud import create_submenu


async def create_dish(id: UUID) -> OutputDishSchema:
    values = {
        "title": "My dish",
        "description": "My submenu dish",
        'price': "10.00",
        'submenu_id': id
    }
    stmt = insert(dish_table).values(**values).returning(dish_table.c.id)
    async with Session() as s:
        id = (await s.execute(stmt)).first()._asdict()['id']
        db_obj = OutputDishSchema(**(await s.execute(select(dish_table).filter_by(id=id))).first()._asdict())
        await s.commit()
    return db_obj


@pytest.mark.asyncio(scope='session')
class TestYDishCrud:

    async def test_post_dish(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.post(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes', json={
                "title": "My dish",
                "description": "My dish description",
                "price": "12.50"
            })
            assert r.status_code == 201
            item = OutputDishSchema(**r.json())
            assert item.title == "My dish"
            assert item.description == "My dish description"
        async with Session() as s:
            db_obj = OutputDishSchema(**(await s.execute(select(dish_table).filter_by(id=item.id))).one()._asdict())
            assert item == db_obj
        await delete_menu(menu.id)

    async def test_get_dish(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        dish = await create_dish(submenu.id)
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}')
            assert r.status_code == 200
            item = OutputDishSchema(**r.json())
            assert dish == item
        await delete_menu(menu.id)

    async def test_get_all_dish(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        await create_dish(submenu.id)
        await create_dish(submenu.id)
        await create_dish(submenu.id)
        async with Session() as s:
            result = await s.execute(select(dish_table).filter_by(submenu_id=submenu.id))
            db_obj_list = [OutputDishSchema(**x._asdict()) for x in result.all()]
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes')
            assert r.status_code == 200
            items_list = [OutputDishSchema(**x) for x in r.json()]
            assert db_obj_list == items_list
        await delete_menu(menu.id)

    async def test_update_dish(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        dish = await create_dish(submenu.id)
        async with AsyncClient() as client:
            r = await client.patch(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}/dishes/{dish.id}',
                json={
                    "title": "My updated dish",
                    "description": "My updated dish description",
                    "price": "9.00"
                })
            assert r.status_code == 200
            item = OutputDishSchema(**r.json())
        async with Session() as s:
            db_obj = OutputDishSchema(**(await s.execute(select(dish_table).filter_by(submenu_id=submenu.id))).one()._asdict())
            assert item == db_obj
        await delete_menu(menu.id)

    async def test_delete_dish(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        dish = await create_dish(submenu.id)
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}')
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(select(dish_table).filter_by(id=dish.id))
            assert result.all() == []
        await delete_menu(menu.id)
