import uuid
from fastapi import APIRouter, HTTPException
from database import Session
from models import MenuOrm
from repositories.menu import MenuRepository
from schemas import MenuSchema

router = APIRouter(
    prefix='/menus',
    tags=['Menu CRUD']
)

menu_repo = MenuRepository(MenuOrm, Session)


@router.get('')
async def get_all_menus():
    m_list = await menu_repo.get_all()
    return menu_repo.to_repr_all(m_list)


@router.get('/{id}')
async def get_menu(id: uuid.UUID):
    resp = await menu_repo.get_one(id)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')

    return menu_repo.to_repr_one(resp)


@router.post('', status_code=201)
async def post_menu(menu: MenuSchema):
    resp = await menu_repo.create_one(menu)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')

    return menu_repo.to_repr_one(resp)


@router.delete('/{id}')
async def delete_menu(id: uuid.UUID):
    await menu_repo.delete_one(id)


@router.patch('/{id}')
async def update_menu(id: uuid.UUID, menu: MenuSchema):
    resp = await menu_repo.update_one(menu, id)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')

    return menu_repo.to_repr_one(resp)

