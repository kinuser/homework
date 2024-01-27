import pytest
from database import Session, async_engine
from models import SubmenuOrm, MenuOrm, Base
from repositories.menu import MenuRepository
from repositories.submenu import SubmenuRepository
from schemas import OutputSubmenuSchema, OutputMenuSchema
from tests.store import SubmenuStore


menu_repo = MenuRepository(MenuOrm, Session)
repo = SubmenuRepository(SubmenuOrm, Session)



@pytest.mark.usefixtures('create_database', 'anyio_backend')
class TestSubMenuRepo:

    async def test_create_menu(self):
        item = OutputMenuSchema(**(await menu_repo.create_one({
            "title": "My menu 1",
            "description": "My menu description 1"
        })))
        assert item.title == 'My menu 1'
        assert item.description == 'My menu description 1'
        SubmenuStore.menu_id = item.id

    async def test_get_all_empty(self):
        resp = await repo.get_all(SubmenuStore.menu_id)
        assert resp == []

    async def test_create(self):
        item = OutputSubmenuSchema(**(await repo.create_one({
            "title": "My submenu 1",
            "description": "My submenu description 1"
        }, SubmenuStore.menu_id)))
        SubmenuStore.add_item(item)
        assert item.title == "My submenu 1"
        assert item.description == "My submenu description 1"
        assert item.menu_id == SubmenuStore.menu_id


    async def test_get(self):
        ritem = OutputSubmenuSchema(**(await repo.get_one(SubmenuStore.litem.id)))
        assert ritem.description == SubmenuStore.litem.description
        assert ritem.title == SubmenuStore.litem.title
        assert ritem.id == SubmenuStore.litem.id
        assert ritem.dishes_count == SubmenuStore.litem.dishes_count
        assert ritem.dishes_count == SubmenuStore.litem.dishes_count

    async def test_get_all(self):
        resp = await repo.get_all(SubmenuStore.menu_id)
        v_resp = [OutputSubmenuSchema(**x) for x in resp]
        t = 0
        while t < len(SubmenuStore.items):
            assert v_resp[t] == SubmenuStore.items[t]
            t = t + 1

    async def test_update(self):
        resp = await repo.update_one({
            "title": "My updated menu",
            "description": "My updated description"
        }, SubmenuStore.litem.id)
        item = OutputSubmenuSchema(**resp)
        SubmenuStore.litem.title = "My updated menu"
        SubmenuStore.litem.description = "My updated description"
        assert item.id == SubmenuStore.litem.id
        assert item.title == SubmenuStore.litem.title
        assert item.description == SubmenuStore.litem.description

    async def test_delete_all(self):
        await repo.delete_one(SubmenuStore.litem.id)
        resp_s = await repo.get_one(SubmenuStore.litem.id)
        SubmenuStore.delete_last()
        await menu_repo.delete_one(SubmenuStore.menu_id)
        resp_m = await menu_repo.get_one(SubmenuStore.menu_id)
        assert resp_s is None
        assert resp_m is None
