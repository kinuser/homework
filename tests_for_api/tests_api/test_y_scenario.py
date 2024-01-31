from httpx import AsyncClient
from sqlalchemy import select
from schemas import OutputMenuSchema, OutputSubmenuSchema, OutputDishSchema
from store import MenuStore, SubmenuStore, DishStore
from config import APP_HOST, APP_PORT
import pytest
from database import Session
from models import dish_table, get_one_menu, get_all_menus, get_all_submenus, get_one_submenu


@pytest.mark.asyncio(scope='session')
class TestYScenario:
    async def test_post_menu(self):
        async with AsyncClient() as client:
            r = await client.post(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus', json={
                "title": "My menu 1",
                "description": "My menu description 1"
            })
            assert r.status_code == 201
            item = OutputMenuSchema(**r.json())
            assert item.title == "My menu 1"
            assert item.description == "My menu description 1"
            MenuStore.add_item(item)
        async with Session() as s:
            db_menu = OutputMenuSchema(**(await s.execute(get_one_menu(item.id))).one()._asdict())
        assert db_menu == item

    async def test_post_submenu(self):
        async with AsyncClient() as client:
            r = await client.post(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus', json={
                "title": "My submenu 1",
                "description": "My submenu description 1"
            })
            assert r.status_code == 201
            item = OutputSubmenuSchema(**r.json())
            assert item.title == "My submenu 1"
            assert item.description == "My submenu description 1"
            SubmenuStore.add_item(item)
        async with Session() as s:
            db_subm = OutputSubmenuSchema(**(await s.execute(get_one_submenu(item.id))).one()._asdict())
        assert item == db_subm

    async def test_post_dish(self):
        async with AsyncClient() as client:
            r = await client.post(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes',
                json={
                    "title": "My dish 1",
                    "description": "My dish description 1",
                    "price": "12.50"
                }
            )
            assert r.status_code == 201
            item = OutputDishSchema(**r.json())
            assert item.title == "My dish 1"
            assert item.description == "My dish description 1"
            assert item.price == "12.50"
            DishStore.add_item(item)
        async with Session() as s:
            db_obj = OutputDishSchema(**(await s.execute(select(dish_table).filter_by(id=item.id))).one()._asdict())
        assert item == db_obj

    async def test_post_dish_2(self):
        async with AsyncClient() as client:
            r = await client.post(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes',
                json={
                    "title": "My dish 2",
                    "description": "My dish description 2",
                    "price": "13.50"
                }
            )
            assert r.status_code == 201
            item = OutputDishSchema(**r.json())
            assert item.title == "My dish 2"
            assert item.description == "My dish description 2"
            assert item.price == "13.50"
            DishStore.add_item(item)
        async with Session() as s:
            db_obj = OutputDishSchema(**(await s.execute(select(dish_table).filter_by(id=item.id))).one()._asdict())
        assert item == db_obj

    async def test_get_menu(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert item.id == MenuStore.litem.id
            assert item.title == MenuStore.litem.title
            assert item.description == MenuStore.litem.description
            assert item.submenus_count == len(SubmenuStore.items)
            assert item.dishes_count == len(DishStore.items)
        async with Session() as s:
            db_menu = OutputMenuSchema(**(await s.execute(get_one_menu(MenuStore.litem.id))).one()._asdict())
        assert db_menu == item

    async def test_get_one_sub(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}')
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
            assert item.id == SubmenuStore.litem.id
            assert item.title == SubmenuStore.litem.title
            assert item.description == SubmenuStore.litem.description
            assert item.dishes_count == len(DishStore.items)
        async with Session() as s:
            db_subm = OutputSubmenuSchema(**(await s.execute(get_one_submenu(item.id))).one()._asdict())
        assert item == db_subm

    async def test_delete_one_sub(self):
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}')
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(get_one_submenu(SubmenuStore.litem.id))
            assert result.all() == []

    async def test_get_all_sub_deleted(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus')
            assert r.status_code == 200
            assert r.json() == []
        async with Session() as s:
            result = await s.execute(get_all_submenus(MenuStore.litem.id))
            assert result.all() == []

    async def test_get_all_dish_deleted(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes')
            assert r.status_code == 200
            assert r.json() == []
        async with Session() as s:
            result = await s.execute(select(dish_table).filter_by(submenu_id=SubmenuStore.litem.id))
            assert result.all() == []
        SubmenuStore.delete_last()
        DishStore.clear()

    async def test_get_one_menu(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert item.id == MenuStore.litem.id
            assert item.title == MenuStore.litem.title
            assert item.description == MenuStore.litem.description
            assert item.submenus_count == len(SubmenuStore.items)
            assert item.dishes_count == len(DishStore.items)
        async with Session() as s:
            db_menu = OutputMenuSchema(**(await s.execute(get_one_menu(MenuStore.litem.id))).one()._asdict())
        assert db_menu == item

    async def test_delete_one_menu(self):
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(get_one_menu(MenuStore.litem.id))
            assert result.all() == []
        MenuStore.delete_last()

    async def test_get_all_menu_empty(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus')
            assert r.status_code == 200
            assert r.json() == []
        async with Session() as s:
            result = await s.execute(get_all_menus())
            assert result.all() == []
