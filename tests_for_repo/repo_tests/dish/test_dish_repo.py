from repositories.dish import DishRepository
from repositories.submenu import SubmenuRepository
from schemas import OutputMenuSchema, OutputSubmenuSchema, OutputDishSchema
from src.database import Session, async_engine
from src.models import MenuOrm, DishOrm, SubmenuOrm, Base
from src.repositories.menu import MenuRepository
from tests.store import MenuStore, DishStore
import pytest

menu_repo = MenuRepository(MenuOrm, Session)
sub_repo = SubmenuRepository(SubmenuOrm, Session)
repo = DishRepository(DishOrm, Session)


@pytest.mark.usefixtures('create_database', 'anyio_backend')
class TestDishRepo:

    async def test_create_menu(self):
        item = OutputMenuSchema(**(await menu_repo.create_one({
            "title": "My menu 1",
            "description": "My menu description 1"
        })))
        assert item.title == 'My menu 1'
        assert item.description == 'My menu description 1'
        DishStore.menu_id = item.id

    async def test_create_submenu(self):
        item = OutputSubmenuSchema(**(await sub_repo.create_one({
            "title": "My submenu 1",
            "description": "My submenu description 1"
        }, DishStore.menu_id)))
        DishStore.submenu_id = item.id
        assert item.title == "My submenu 1"
        assert item.description == "My submenu description 1"
        assert item.menu_id == DishStore.menu_id

    async def test_get_all_empty(self):
        resp = await repo.get_all(DishStore.submenu_id)
        assert resp == []

    async def test_create(self):
        item = OutputDishSchema(**(await repo.create_one({
            "title": "My dish 1",
            "description": "My dish description 1",
            "price": "12.50"
        }, DishStore.submenu_id)))
        assert item.title == "My dish 1"
        assert item.description == "My dish description 1"
        DishStore.add_item(item)

    async def test_get(self):
        ritem = OutputDishSchema(**(await repo.get_one(DishStore.litem.id)))
        assert ritem.description == DishStore.litem.description
        assert ritem.title == DishStore.litem.title
        assert ritem.id == DishStore.litem.id
        assert ritem.price == DishStore.litem.price
        assert ritem.submenu_id == DishStore.litem.submenu_id

    async def test_get_all(self):
        resp = await repo.get_all(DishStore.submenu_id)
        v_resp = [OutputDishSchema(**x) for x in resp]
        t = 0
        while t < len(DishStore.items):
            assert v_resp[t] == DishStore.items[t]
            t = t + 1

    async def test_update(self):
        resp = await repo.update_one({
            "title": "My updated dish",
            "description": "My updated description"
        }, DishStore.litem.id)
        item = OutputDishSchema(**resp)
        DishStore.litem.title = "My updated dish"
        DishStore.litem.description = "My updated description"
        assert item.id == DishStore.litem.id
        assert item.title == DishStore.litem.title
        assert item.description == DishStore.litem.description

    async def test_delete_all(self):
        await repo.delete_one(DishStore.litem.id)
        resp_d = await repo.get_one(DishStore.litem.id)
        DishStore.delete_last()
        await sub_repo.delete_one(DishStore.submenu_id)
        resp_s = await sub_repo.get_one(DishStore.submenu_id)
        await menu_repo.delete_one(DishStore.menu_id)
        resp_m = await menu_repo.get_one(DishStore.menu_id)
        assert resp_d is None
        assert resp_s is None
        assert resp_m is None
