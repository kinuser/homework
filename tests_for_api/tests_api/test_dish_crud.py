from httpx import AsyncClient
from schemas import OutputMenuSchema, OutputSubmenuSchema, OutputDishSchema
from store import MenuStore, SubmenuStore, DishStore
import pytest
from config import APP_HOST, APP_PORT


@pytest.mark.asyncio(scope='session')
class TestSubmenuCRUD:

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

    async def test_get_all_empty_dish(self):
        async with AsyncClient() as client:
            r = await client.get(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes'
            )
            assert r.status_code == 200
            assert r.json() == []

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

    async def test_get_all_dish(self):
        async with AsyncClient() as client:
            r = await client.get(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes'
            )
            assert r.status_code == 200
            rl: list = r.json()
            assert len(rl) == 1
            item = OutputDishSchema(**rl[0])
            assert item.id == DishStore.litem.id
            assert item.title == DishStore.litem.title
            assert item.description == DishStore.litem.description
            assert item.price == DishStore.litem.price

    async def test_get_one_dish(self):
        async with AsyncClient() as client:
            r = await client.get(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes/{DishStore.litem.id}'
            )
            assert r.status_code == 200
            item = OutputDishSchema(**r.json())
            assert item.id == DishStore.litem.id
            assert item.title == DishStore.litem.title
            assert item.description == DishStore.litem.description
            assert item.price == DishStore.litem.price

    async def test_patch_dish(self):
        async with AsyncClient() as client:
            r = await client.patch(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes/{DishStore.litem.id}',
                json={
                    "title": "My updated dish 1",
                    "description": "My updated dish description 1",
                    "price": "14.50"
                })
            assert r.status_code == 200
            item = OutputDishSchema(**r.json())
            assert item.id == DishStore.litem.id
            assert item.title == "My updated dish 1"
            assert item.description == "My updated dish description 1"
            assert item.price == "14.50"
            DishStore.delete_last()
            DishStore.add_item(item)

    async def test_get_patched_dish(self):
        async with AsyncClient() as client:
            r = await client.get(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes/{DishStore.litem.id}'
            )
            assert r.status_code == 200
            item = OutputDishSchema(**r.json())
            assert item.id == DishStore.litem.id
            assert item.title == DishStore.litem.title
            assert item.description == DishStore.litem.description
            assert item.price == DishStore.litem.price

    async def test_delete_one_dish(self):
        async with AsyncClient() as client:
            r = await client.delete(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes/{DishStore.litem.id}',
            )
            assert r.status_code == 200

    async def test_get_all_dish_deleted(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes')
            assert r.status_code == 200
            assert r.json() == []

    async def test_get_one_dish_error(self):
        async with AsyncClient() as client:
            r = await client.get(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}/dishes/{DishStore.litem.id}'
            )
            assert r.status_code == 404
            assert r.json()['detail'] == 'dish not found'

    async def test_delete_one_submenu(self):
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}')
            assert r.status_code == 200

    async def test_get_all_submenu_deleted(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus')
            assert r.status_code == 200
            assert r.json() == []

    async def test_delete_one_menu(self):
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 200

    async def test_get_all_menu_deleted(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus')
            assert r.status_code == 200
            assert r.json() == []
            MenuStore.delete_last()
            SubmenuStore.delete_last()
            DishStore.delete_last()
