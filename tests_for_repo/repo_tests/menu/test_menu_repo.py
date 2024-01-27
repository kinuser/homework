from schemas import OutputMenuSchema
from src.database import Session, async_engine
from src.models import MenuOrm, Base
from src.repositories.menu import MenuRepository
from tests.store import MenuStore
import pytest


repo = MenuRepository(MenuOrm, Session)


@pytest.mark.usefixtures('create_database', 'anyio_backend')
class TestMenuRepo:

    async def test_get_all_empty(self):
        resp = await repo.get_all()
        assert resp == []
        self.var = 1

    async def test_create(self):
        item = OutputMenuSchema(**(await repo.create_one({
            "title": "My menu 1",
            "description": "My menu description 1"
        })))
        assert item.title == 'My menu 1'
        assert item.description == 'My menu description 1'
        MenuStore.add_item(item)

    async def test_get(self):
        ritem = OutputMenuSchema(**(await repo.get_one(MenuStore.litem.id)))
        assert ritem.description == MenuStore.litem.description
        assert ritem.title == MenuStore.litem.title
        assert ritem.id == MenuStore.litem.id
        assert ritem.dishes_count == MenuStore.litem.dishes_count
        assert ritem.submenus_count == MenuStore.litem.submenus_count

    async def test_get_all(self):
        resp = await repo.get_all()
        v_resp = [OutputMenuSchema(**x) for x in resp]
        t = 0
        while t < len(MenuStore.items):
            assert v_resp[t] == MenuStore.items[t]
            t = t + 1

    async def test_update(self):
        resp = await repo.update_one({
            "title": "My updated menu",
            "description": "My updated description"
        }, MenuStore.litem.id)
        item = OutputMenuSchema(**resp)
        MenuStore.litem.title = "My updated menu"
        MenuStore.litem.description = "My updated description"
        assert item.id == MenuStore.litem.id
        assert item.title == MenuStore.litem.title
        assert item.description == MenuStore.litem.description

    async def test_delete(self):
        await repo.delete_one(MenuStore.litem.id)
        resp = await repo.get_one(MenuStore.litem.id)
        MenuStore.delete_last()
        assert resp is None

