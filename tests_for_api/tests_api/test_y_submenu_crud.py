from uuid import UUID
from httpx import AsyncClient
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError
from schemas import OutputSubmenuSchema
from config import APP_HOST, APP_PORT
from models import submenu_table, get_one_submenu, get_all_submenus
from database import Session
import pytest

from test_y_menu_crud import create_menu, delete_menu


async def create_submenu(id: UUID) -> OutputSubmenuSchema:
    values = {
        "title": "My submenu",
        "description": "My submenu description",
        'menu_id': id
    }
    stmt = insert(submenu_table).values(**values).returning(submenu_table.c.id)
    async with Session() as s:
        dict_id = (await s.execute(stmt)).first()._asdict()
        db_obj = OutputSubmenuSchema(**(await s.execute(get_one_submenu(dict_id['id']))).first()._asdict())
        await s.commit()
    return db_obj


@pytest.mark.asyncio(scope='session')
class TestYSubmenuCRUD:
    async def test_post_submenu(self):
        menu = await create_menu()
        async with AsyncClient() as client:
            r = await client.post(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus', json={
                "title": "My submenu 1",
                "description": "My submenu description 1"
            })
            assert r.status_code == 201
            item = OutputSubmenuSchema(**r.json())
            assert item.title == "My submenu 1"
            assert item.description == "My submenu description 1"
        async with Session() as s:
            db_subm = OutputSubmenuSchema(**(await s.execute(get_one_submenu(item.id))).one()._asdict())
            assert item == db_subm
        await delete_menu(menu.id)

    async def test_get_submenu(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}')
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
            assert submenu == item
        await delete_menu(menu.id)

    async def test_get_all_submenus(self):
        menu = await create_menu()
        subm_1 = await create_submenu(menu.id)
        subm_2 = await create_submenu(menu.id)
        async with Session() as s:
            print(get_all_submenus(menu.id).compile(compile_kwargs={"literal_binds": True}))
            result = await s.execute(get_all_submenus(menu.id))
            db_obj_list = [OutputSubmenuSchema(**x._asdict()) for x in result.all()]
            async with AsyncClient() as client:
                r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus')
                assert r.status_code == 200
                items_list = [OutputSubmenuSchema(**x) for x in r.json()]
                assert db_obj_list == items_list
        await delete_menu(menu.id)

    async def test_update_submenu(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.patch(
                f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}',
                json={
                    "title": "My updated submenu 1",
                    "description": "My updated submenu description 1"
                })
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
        async with Session() as s:
            db_obj = OutputSubmenuSchema(**(await s.execute(get_one_submenu(item.id))).one()._asdict())
            assert item == db_obj
        await delete_menu(menu.id)

    async def test_delete_submenu(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{menu.id}/submenus/{submenu.id}')
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(get_one_submenu(submenu.id))
            assert result.all() == []
        await delete_menu(menu.id)