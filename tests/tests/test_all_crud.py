import pytest
from httpx import AsyncClient

from db_dependencies.uofs import AllUOF
from tests.test_schemas import MenuSchemaAll
from tests.test_y_dish_crud import create_dish
from tests.test_y_menu_crud import create_menu, delete_menu
from tests.test_y_submenu_crud import create_submenu
from utils import reverse


@pytest.mark.asyncio(scope='session')
class TestYMenuCrud:
    """
    Group of CRUD tests for testing menu.
    Every test are fully independent
    """
    async def test_post_menu(self):
        """Testing post"""
        async with AsyncClient() as client:
            menu = await create_menu()
            submenu = await create_submenu(menu.id)
            await create_dish(menu.id, submenu.id)
            await create_dish(menu.id, submenu.id)
            await create_dish(menu.id, submenu.id)
            r = await client.get(reverse('get_everything'))
            assert r.status_code == 200
            items = [MenuSchemaAll(**x) for x in r.json()]
            db_items = await AllUOF.get_everything()
            assert db_items == items
            await delete_menu(menu.id)
