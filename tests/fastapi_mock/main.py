import uuid
from uuid import UUID

from fastapi import APIRouter, FastAPI

from tests.test_schemas import DishSchema, MenuSchema, SubmenuSchema

app = FastAPI()


main_router = APIRouter(
    prefix='/api/v1'
)


menu_router = APIRouter(
    prefix='/menus',
    tags=['Menu CRUD']
)


@menu_router.get('')
async def get_all_menus() -> None:
    """Get all menus"""


@menu_router.get('/{menu_id}')
async def get_menu(menu_id: uuid.UUID) -> None:
    """Get one menu by id"""


@menu_router.post('')
async def post_menu(menu: MenuSchema) -> None:
    """Create one menu"""
    pass


@menu_router.delete('/{menu_id}')
async def delete_menu(menu_id: uuid.UUID) -> None:
    """Delete one menu"""


@menu_router.patch('/{menu_id}')
async def update_menu(menu_id: uuid.UUID, menu: MenuSchema) -> None:
    """Delete one menu"""

submenu_router = APIRouter(
    prefix='/menus',
    tags=['Submenu CRUD']
)

SUBM_ROUTE = '/{menu_id}/submenus'


@submenu_router.get(SUBM_ROUTE)
async def get_all_submenus(menu_id: UUID) -> None:
    """Get all submenus"""


@submenu_router.get(SUBM_ROUTE + '/{submenu_id}')
async def get_submenu(menu_id: UUID, submenu_id: UUID) -> None:
    """Get one submenu by id"""


@submenu_router.post(SUBM_ROUTE)
async def post_submenu(menu_id: UUID, submenu: SubmenuSchema) -> None:
    """Create one submenu"""


@submenu_router.delete(SUBM_ROUTE + '/{submenu_id}')
async def delete_submenu(menu_id: UUID, submenu_id: UUID) -> None:
    """Delete one submenu"""


@submenu_router.patch(SUBM_ROUTE + '/{submenu_id}',)
async def update_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuSchema) -> None:
    """Delete one submenu"""

dish_router = APIRouter(
    prefix='/menus',
    tags=['Dish CRUD']
)

DISH_PATH = '/{menu_id}/submenus/{submenu_id}/dishes'


@dish_router.get(DISH_PATH)
async def get_all_dishes(menu_id: UUID, submenu_id: UUID) -> None:
    """Get all dishes"""


@dish_router.get(DISH_PATH + '/{dish_id}')
async def get_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> None:
    """Get one dish by id"""


@dish_router.post(DISH_PATH)
async def post_dish(menu_id: UUID, submenu_id: UUID, dish: DishSchema) -> None:
    """Create one dish"""


@dish_router.delete(DISH_PATH + '/{dish_id}')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> None:
    """Delete one dish"""


@dish_router.patch(DISH_PATH + '/{dish_id}')
async def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: DishSchema) -> None:
    """Delete one dish"""


main_router.include_router(menu_router)
main_router.include_router(submenu_router)
main_router.include_router(dish_router)
app.include_router(main_router)
