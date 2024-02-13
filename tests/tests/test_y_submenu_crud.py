import asyncio
from uuid import UUID

import pytest
from db_dependencies.database import Session
from db_dependencies.models import get_all_submenus, get_one_submenu
from db_dependencies.redis_repos import SubmenuRedisRepo
from db_dependencies.submenu import SubmenuRepository
from db_dependencies.uofs import SubmenuUOF
from httpx import AsyncClient
from utils import reverse

from tests.test_schemas import OutputSubmenuSchema, SubmenuSchema
from tests.test_y_menu_crud import create_menu, delete_menu


async def create_submenu(m_id: UUID) -> OutputSubmenuSchema | None:
    values = {
        'title': 'My submenu',
        'description': 'My submenu description',
        'menu_id': m_id
    }
    resp = await SubmenuUOF.create(m_id, SubmenuSchema(**values))
    if resp:
        return resp
    return None


async def get_db_smenu(sm_id: UUID) -> OutputSubmenuSchema | None:
    async with Session() as s:
        res = await SubmenuRepository(s).get_one(sm_id)
    if res:
        return res
    return None


async def get_cache_smenu(m_id: UUID, sm_id: UUID) -> OutputSubmenuSchema | None:
    res = await SubmenuUOF.get(m_id, sm_id)
    if res:
        return res
    return None


@pytest.mark.asyncio(scope='session')
class TestYSubmenuCRUD:
    async def test_post_submenu(self):
        menu = await create_menu()
        async with AsyncClient() as client:
            r = await client.post(
                reverse('post_submenu', menu.id),
                json={
                    'title': 'My submenu 1',
                    'description': 'My submenu description 1'
                }
            )
            assert r.status_code == 201
            item = OutputSubmenuSchema(**r.json())
            assert item.title == 'My submenu 1'
            assert item.description == 'My submenu description 1'
        db_subm = await get_db_smenu(item.id)
        await asyncio.sleep(1)
        ch_subm = await get_cache_smenu(menu.id, item.id)
        assert item == db_subm == ch_subm
        await delete_menu(menu.id)

    async def test_get_submenu(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.get(
                reverse('get_submenu', menu.id, submenu.id)
            )
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
            assert submenu == item
        await delete_menu(menu.id)

    async def test_get_all_submenus(self):
        menu = await create_menu()
        await create_submenu(menu.id)
        await create_submenu(menu.id)
        async with Session() as s:
            result = await s.execute(get_all_submenus(menu.id))
            db_obj_list = [
                OutputSubmenuSchema(**x._asdict()) for x in result.all()
            ]
            cache_obj_list = [
                x for x in await SubmenuRedisRepo.get_all(menu.id)
            ]
            async with AsyncClient() as client:
                r = await client.get(
                    reverse('get_all_submenus', menu.id)
                )
                assert r.status_code == 200
                items_list = [OutputSubmenuSchema(**x) for x in r.json()]
                db_obj_list = sorted(db_obj_list, key=lambda x: x.id, reverse=True)
                items_list = sorted(items_list, key=lambda x: x.id, reverse=True)
                cache_obj_list = sorted(cache_obj_list, key=lambda x: x.id, reverse=True)
                assert db_obj_list == items_list == cache_obj_list
        await delete_menu(menu.id)

    async def test_update_submenu(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.patch(
                reverse('update_submenu', menu.id, submenu.id),
                json={
                    'title': 'My updated submenu 1',
                    'description': 'My updated submenu description 1'
                })
            assert r.status_code == 200
            item = OutputSubmenuSchema(**r.json())
        db_obj = await get_db_smenu(submenu.id)
        await asyncio.sleep(1)
        cache_obj = await get_cache_smenu(menu.id, submenu.id)
        assert item == db_obj == cache_obj
        await delete_menu(menu.id)

    async def test_delete_submenu(self):
        menu = await create_menu()
        submenu = await create_submenu(menu.id)
        async with AsyncClient() as client:
            r = await client.delete(
                reverse('delete_submenu', menu.id, submenu.id)
            )
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(get_one_submenu(submenu.id))
            await asyncio.sleep(1)
            cache_resp = await SubmenuUOF.get(menu.id, submenu.id)
            assert cache_resp is None
            assert result.all() == []
        await delete_menu(menu.id)
