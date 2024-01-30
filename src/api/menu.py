import uuid
from fastapi import APIRouter, HTTPException
from database import Session
from models import menu_table
from repositories.menu import MenuRepository
from schemas import MenuSchema

router = APIRouter(
    prefix='/menus',
    tags=['Menu CRUD']
)

menu_repo = MenuRepository(menu_table, Session)


@router.get('')
async def get_all_menus():
    return await menu_repo.get_all()


@router.get('/{id}')
async def get_menu(id: uuid.UUID):
    resp = await menu_repo.get_one(id)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')
    return resp


@router.post('', status_code=201)
async def post_menu(menu: MenuSchema):
    return await menu_repo.create_one(menu.model_dump())


@router.delete('/{id}')
async def delete_menu(id: uuid.UUID):
    if await menu_repo.delete_one(id):
        return
    else:
        raise HTTPException(status_code=404, detail='menu not found')


@router.patch('/{id}')
async def update_menu(id: uuid.UUID, menu: MenuSchema):
    resp = await menu_repo.update_one(menu.model_dump(), id)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')
    return resp

