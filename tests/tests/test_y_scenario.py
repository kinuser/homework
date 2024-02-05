"""Test scenario for checking counters"""
import pytest
from db_dependencies.database import Session
from db_dependencies.menu import get_all_menus, get_one_menu
from db_dependencies.models import dish_table
from db_dependencies.submenu import get_all_submenu, get_one_submenu
from httpx import AsyncClient
from sqlalchemy import select
from utils import reverse

from tests.store import DishStore, MenuStore, SubmenuStore
from tests.test_schemas import OutputDishSchema, OutputMenuSchema, OutputSubmenuSchema


@pytest.mark.asyncio(scope='session')
class TestYScenario:
    """Class for scenario execution"""
    async def test_post_menu(self):
        """Create menu"""
        async with AsyncClient() as client:
            r = await client.post(reverse('menu'), json={
                'title': 'My menu 1',
                'description': 'My menu description 1'
            })
            assert r.status_code == 201
            item = OutputMenuSchema(**r.json())
            assert item.title == 'My menu 1'
            assert item.description == 'My menu description 1'
            MenuStore.add_item(item)
        async with Session() as s:
            db_menu = OutputMenuSchema(**(await s.execute(get_one_menu(item.id))).one()._asdict())
        assert db_menu == item

    async def test_post_submenu(self):
        """Create submenu"""
        async with AsyncClient() as client:
            r = await client.post(reverse('submenu', MenuStore.litem.id), json={
                'title': 'My submenu 1',
                'description': 'My submenu description 1'
            })
            assert r.status_code == 201
            item = OutputSubmenuSchema(**r.json())
            assert item.title == 'My submenu 1'
            assert item.description == 'My submenu description 1'
            SubmenuStore.add_item(item)
        async with Session() as s:
            db_subm = OutputSubmenuSchema(
                **(await s.execute(get_one_submenu(item.id))).one()._asdict()
            )
        assert item == db_subm

    async def test_post_dish(self):
        """Create dish"""
        async with AsyncClient() as client:
            r = await client.post(
                reverse('dish', MenuStore.litem.id, SubmenuStore.litem.id),
                json={
                    'title': 'My dish 1',
                    'description': 'My dish description 1',
                    'price': '12.50'
                }
            )
            assert r.status_code == 201
            item = OutputDishSchema(**r.json())
            assert item.title == 'My dish 1'
            assert item.description == 'My dish description 1'
            assert item.price == '12.50'
            DishStore.add_item(item)
        async with Session() as s:
            db_obj = OutputDishSchema(**(await s.execute(select(dish_table).filter_by(id=item.id))).one()._asdict())
        assert item == db_obj

    async def test_post_dish_2(self):
        """Create dish 2"""
        async with AsyncClient() as client:
            r = await client.post(
                reverse('dish', MenuStore.litem.id, SubmenuStore.litem.id),
                json={
                    'title': 'My dish 2',
                    'description': 'My dish description 2',
                    'price': '13.50'
                }
            )
            assert r.status_code == 201
            item = OutputDishSchema(**r.json())
            assert item.title == 'My dish 2'
            assert item.description == 'My dish description 2'
            assert item.price == '13.50'
            DishStore.add_item(item)
        async with Session() as s:
            db_obj = OutputDishSchema(**(await s.execute(select(dish_table).filter_by(id=item.id))).one()._asdict())
        assert item == db_obj

    async def test_get_menu(self):
        """Get menu"""
        async with AsyncClient() as client:
            r = await client.get(reverse('menu', MenuStore.litem.id))
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
        """Get submenu"""
        async with AsyncClient() as client:
            r = await client.get(reverse('submenu', MenuStore.litem.id, SubmenuStore.litem.id))
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
        """Delete one submenu"""
        async with AsyncClient() as client:
            r = await client.delete(reverse('submenu', MenuStore.litem.id, SubmenuStore.litem.id))
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(get_one_submenu(SubmenuStore.litem.id))
            assert result.all() == []

    async def test_get_all_sub_deleted(self):
        """Get empty submenus list"""
        async with AsyncClient() as client:
            r = await client.get(reverse('submenu', MenuStore.litem.id))
            assert r.status_code == 200
            assert r.json() == []
        async with Session() as s:
            result = await s.execute(get_all_submenu(MenuStore.litem.id))
            assert result.all() == []

    async def test_get_all_dish_deleted(self):
        """Get empty dishes list"""
        async with AsyncClient() as client:
            r = await client.get(reverse('dish', MenuStore.litem.id, SubmenuStore.litem.id))
            assert r.status_code == 200
            assert r.json() == []
        async with Session() as s:
            result = await s.execute(select(dish_table).filter_by(submenu_id=SubmenuStore.litem.id))
            assert result.all() == []
        SubmenuStore.delete_last()
        DishStore.clear()

    async def test_get_one_menu(self):
        """Get 1 menu"""
        async with AsyncClient() as client:
            r = await client.get(reverse('menu', MenuStore.litem.id))
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
        """Delete menu"""
        async with AsyncClient() as client:
            r = await client.delete(reverse('menu', MenuStore.litem.id))
            assert r.status_code == 200
        async with Session() as s:
            result = await s.execute(get_one_menu(MenuStore.litem.id))
            assert result.all() == []
        MenuStore.delete_last()

    async def test_get_all_menu_empty(self):
        """Get empty list"""
        async with AsyncClient() as client:
            r = await client.get(reverse('menu'))
            assert r.status_code == 200
            assert r.json() == []
        async with Session() as s:
            result = await s.execute(get_all_menus())
            assert result.all() == []
