"""Module contains dish API"""
from uuid import UUID

from fastapi import APIRouter, HTTPException

from schemas import DishSchema
from uof.uofs import DishesUOF

router = APIRouter(
    prefix='/menus',
    tags=['Dish CRUD']
)

PARENT = '/{menu_id}/submenus/{submenu_id}/dishes'


@router.get(PARENT)
async def get_all_dishes(menu_id: UUID, submenu_id: UUID) -> list:
    """Get all dishes"""
    return await DishesUOF.get_all(menu_id, submenu_id)


@router.get(PARENT + '/{dish_id}')
async def get_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> dict:
    """Get one dish by id"""
    resp = await DishesUOF.get(menu_id, submenu_id, dish_id)
    if not resp:
        raise HTTPException(status_code=404, detail='dish not found')
    return resp


@router.post(PARENT, status_code=201)
async def post_dish(menu_id: UUID, submenu_id: UUID, dish: DishSchema) -> dict:
    """Create one dish"""
    resp = await DishesUOF.create(menu_id, submenu_id, dish.model_dump())
    if not resp:
        raise HTTPException(status_code=404, detail='submenu not found')
    return resp


@router.delete(PARENT + '/{dish_id}')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> None:
    """Delete one dish"""
    if await DishesUOF.delete(menu_id, submenu_id, dish_id):
        return
    raise HTTPException(status_code=404, detail='menu not found')


@router.patch(PARENT + '/{dish_id}')
async def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish: DishSchema) -> dict:
    """Delete one dish"""
    resp = await DishesUOF.update(menu_id, submenu_id, dish_id, dish.model_dump())
    if not resp:
        raise HTTPException(status_code=404, detail='dish not found')
    return resp
