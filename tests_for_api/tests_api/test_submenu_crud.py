from httpx import AsyncClient
from schemas import OutputMenuSchema, OutputSubmenuSchema
from store import MenuStore, SubmenuStore
from config import APP_HOST, APP_PORT
import pytest


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

    async def test_get_all_empty_sub(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus')
            assert r.status_code == 200
            assert r.json() == []

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

    async def test_get_all_sub(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus')
            assert r.status_code == 200
            rl: list = r.json()
            assert len(rl) == 1
            item = OutputSubmenuSchema(**rl[0])
            assert item.id == SubmenuStore.litem.id
            assert item.title == SubmenuStore.litem.title
            assert item.description == SubmenuStore.litem.description
            assert item.dishes_count == SubmenuStore.litem.dishes_count

    async def test_get_one_sub(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}')
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
            assert item.id == SubmenuStore.litem.id
            assert item.title == SubmenuStore.litem.title
            assert item.description == SubmenuStore.litem.description
            assert item.dishes_count == SubmenuStore.litem.dishes_count

    async def test_patch_sub(self):
        async with AsyncClient() as client:
            r = await client.patch(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}',
                json={
                    "title": "My updated submenu 1",
                    "description": "My updated submenu description 1"
                })
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
            assert item.id == SubmenuStore.litem.id
            assert item.title == "My updated submenu 1"
            assert item.description == "My updated submenu description 1"
            assert item.dishes_count == SubmenuStore.litem.dishes_count
            SubmenuStore.delete_last()
            SubmenuStore.add_item(item)

    async def test_get_patched_sub(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}')
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
            assert item.id == SubmenuStore.litem.id
            assert item.title == SubmenuStore.litem.title
            assert item.description == SubmenuStore.litem.description
            assert item.dishes_count == SubmenuStore.litem.dishes_count

    async def test_delete_one_sub(self):
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}')
            assert r.status_code == 200

    async def test_get_all_sub_deleted(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus')
            assert r.status_code == 200
            assert r.json() == []

    async def test_get_one_sub_error(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}/submenus/{SubmenuStore.litem.id}')
            assert r.status_code == 404
            assert r.json()['detail'] == 'submenu not found'

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


