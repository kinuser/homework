from uuid import UUID
from httpx import AsyncClient
from sqlalchemy import insert, update, delete
from sqlalchemy.exc import IntegrityError

from config import APP_HOST, APP_PORT
from database import Session
from models import menu_table, get_one_menu, get_all_menus
from schemas import OutputMenuSchema
import pytest


async def create_menu() -> OutputMenuSchema:
    values = {
        "title": "My menu",
        "description": "My menu description"
    }
    stmt = insert(menu_table).values(**values).returning(menu_table.c.id)
    async with Session() as s:
        dict_id = (await s.execute(stmt)).first()._asdict()
        db_obj = OutputMenuSchema(**(await s.execute(get_one_menu(dict_id['id']))).first()._asdict())
        await s.commit()
        return db_obj


async def delete_menu(id: UUID):
    stmt = delete(menu_table).filter_by(id=id)
    async with Session() as s:
        try:
            await s.execute(stmt)
            await s.commit()
            return True
        except IntegrityError:
            return None


@pytest.mark.asyncio(scope='session')
class TestYMenuCrud:
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
        async with Session() as s:
            db_menu = OutputMenuSchema(**(await s.execute(get_one_menu(item.id))).one()._asdict())
            assert db_menu == item
        await delete_menu(db_menu.id)

    async def test_get_menu(self):
        db_menu = await create_menu()
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{db_menu.id}')
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert db_menu == item
        await delete_menu(db_menu.id)

    async def test_get_all_menus(self):
        menu_1 = await create_menu()
        menu_2 = await create_menu()
        menu_3 = await create_menu()
        async with Session() as s:
            result = await s.execute(get_all_menus())
            db_obj_list = [OutputMenuSchema(**x._asdict()) for x in result.all()]
            async with AsyncClient() as client:
                r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus')
                assert r.status_code == 200
                items_list = [OutputMenuSchema(**x) for x in r.json()]
                assert db_obj_list == items_list
        await delete_menu(menu_1.id)
        await delete_menu(menu_2.id)
        await delete_menu(menu_3.id)

    async def test_update_menu(self):
        values = {
            "title": "My menu 1",
            "description": "My menu description 1"
        }
        stmt = insert(menu_table).values(**values).returning(menu_table.c.id)
        async with Session() as s:
            id = (await s.execute(stmt)).first()._asdict()['id']
            values = {
                "title": "My updated menu 1",
                "description": "My updated menu description 1"
            }
            stmt2 = (update(menu_table)
                     .values(**values)
                     .where(menu_table.c.id == id)
                     .returning(menu_table.c.id))
            id = (await s.execute(stmt2)).first()._asdict()['id']
            dm_menu = OutputMenuSchema(**(await s.execute(get_one_menu(id))).first()._asdict())
            await s.commit()
        async with AsyncClient() as client:
            r = await client.get(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{id}')
            assert r.status_code == 200
            item = OutputMenuSchema(**r.json())
            assert item.title == values['title']
            assert item.description == values['description']
            assert dm_menu == item
        await delete_menu(dm_menu.id)

    async def test_delete_menu(self):
        db_menu = await create_menu()
        async with AsyncClient() as client:
            r = await client.delete(f'http://{APP_HOST}:{APP_PORT}/api/v1/menus/{db_menu.id}')
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(get_one_menu(db_menu.id))
            assert result.all() == []
