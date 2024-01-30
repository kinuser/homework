from uuid import UUID
from fastapi import APIRouter, HTTPException
from database import Session
from models import dish_table
from repositories.dish import DishRepository
from schemas import DishSchema

router = APIRouter(
    prefix='/menus',
    tags=['Dish CRUD']
)

submenu_repo = DishRepository(dish_table, Session)

perm_string = '/{menu_id}/submenus/{submenu_id}/dishes'


@router.get(perm_string)
async def get_all_dishes(menu_id: UUID, submenu_id: UUID):
    return await submenu_repo.get_all(submenu_id)


@router.get(perm_string + '/{dish_id}')
async def get_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID):
    resp = await submenu_repo.get_one(dish_id)
    if not resp:
        raise HTTPException(status_code=404, detail='dish not found')
    return resp


@router.post(perm_string, status_code=201)
async def post_dish(menu_id: UUID, submenu_id: UUID, dish: DishSchema):
    resp = await submenu_repo.create_one(dish.model_dump(), submenu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='submenu not found')
    return resp


@router.delete(perm_string + '/{dish_id}')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID):
    if await submenu_repo.delete_one(dish_id):
        return
    else:
        raise HTTPException(status_code=404, detail='menu not found')


@router.patch(perm_string + '/{dish_id}')
async def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: DishSchema):
    resp = await submenu_repo.update_one(dish.model_dump(),  dish_id)
    if not resp:
        raise HTTPException(status_code=404, detail='dish not found')
    return resp