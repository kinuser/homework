from fastapi import APIRouter
from api.menu import router as menu_router
from api.submenu import router as submenu_router
from api.dish import router as dish_router


main_router = APIRouter(
    prefix='/api/v1'
)

main_router.include_router(menu_router)
main_router.include_router(submenu_router)
main_router.include_router(dish_router)
