from uuid import UUID
from fastapi import APIRouter, HTTPException
from database import Session
from models import DishOrm
from repositories.dish import DishRepository
from schemas import DishSchema

router = APIRouter(
    prefix='/menus',
    tags=['Dish CRUD']
)

dish_repo = DishRepository(DishOrm, Session)

perm_string = '/{menu_id}/submenus/{submenu_id}/dishes'


@router.get(perm_string)
async def get_all_dishes(menu_id: UUID, submenu_id: UUID):
    return await dish_repo.get_all(submenu_id)


@router.get(perm_string + '/{dish_id}')
async def get_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID):
    resp = await dish_repo.get_one(dish_id)
    if not resp:
        raise HTTPException(status_code=404, detail='dish not found')
    return resp


@router.post(perm_string, status_code=201)
async def post_dish(menu_id: UUID, submenu_id: UUID, submenu: DishSchema):
    resp = await dish_repo.create_one(submenu.model_dump(), submenu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='submenu not found')
    return resp


@router.delete(perm_string + '/{dish_id}')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID):
    await dish_repo.delete_one(dish_id)


@router.patch(perm_string + '/{dish_id}')
async def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, submenu: DishSchema):
    resp = await dish_repo.update_one(submenu.model_dump(), dish_id)
    if not resp:
        raise HTTPException(status_code=404, detail='dish not found')
    return resp
