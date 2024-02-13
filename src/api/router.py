"""Module connects routers to app"""
from fastapi import APIRouter

from api.dish import router as dish_router
from api.menu import router as menu_router
from api.submenu import router as submenu_router
from schemas import MenuSchemaAll
from uof.uofs import AllUOF

main_router = APIRouter(
    prefix='/api/v1'
)

main_router.include_router(menu_router)
main_router.include_router(submenu_router)
main_router.include_router(dish_router)


@main_router.get(
    '/all',
    response_model=list[MenuSchemaAll],
    tags=['get', 'ALL']
)
async def get_everything() -> list[MenuSchemaAll]:
    """Get all menus"""
    return await AllUOF.get_everything()
