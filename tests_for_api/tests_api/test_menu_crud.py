from httpx import AsyncClient
from schemas import OutputMenuSchema
from store import MenuStore
from config import APP_HOST, APP_PORT
import pytest


@pytest.mark.usefixtures('anyio_backend')
class TestMenuCRUD:

    async def test_get_all_empty(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus')
            assert r.status_code == 200
            assert r.json() == []

    async def test_post(self):
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

    async def test_getall(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus')
            assert r.status_code == 200
            rl: list = r.json()
            assert len(rl) == 1
            item = OutputMenuSchema(**rl[0])
            assert item.id == MenuStore.litem.id
            assert item.title == MenuStore.litem.title
            assert item.description == MenuStore.litem.description
            assert item.submenus_count == MenuStore.litem.submenus_count
            assert item.dishes_count == MenuStore.litem.dishes_count

    async def test_get_one(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert item.id == MenuStore.litem.id
            assert item.title == MenuStore.litem.title
            assert item.description == MenuStore.litem.description
            assert item.submenus_count == MenuStore.litem.submenus_count
            assert item.dishes_count == MenuStore.litem.dishes_count

    async def test_patch(self):
        async with AsyncClient() as client:
            r = await client.patch(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}', json={
                "title": "My updated menu 1",
                "description": "My updated menu description 1"
            })
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert item.id == MenuStore.litem.id
            assert item.title == "My updated menu 1"
            assert item.description == "My updated menu description 1"
            assert item.submenus_count == MenuStore.litem.submenus_count
            assert item.dishes_count == MenuStore.litem.dishes_count
            MenuStore.delete_last()
            MenuStore.add_item(item)

    async def test_get_patched(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert item.id == MenuStore.litem.id
            assert item.title == MenuStore.litem.title
            assert item.description == MenuStore.litem.description
            assert item.submenus_count == MenuStore.litem.submenus_count
            assert item.dishes_count == MenuStore.litem.dishes_count

    async def test_delete_one(self):
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 200

    async def test_get_all_deleted(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus')
            assert r.status_code == 200
            assert r.json() == []

    async def test_get_one_error(self):
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{MenuStore.litem.id}')
            assert r.status_code == 404
            assert r.json()['detail'] == 'menu not found'
            MenuStore.delete_last()
