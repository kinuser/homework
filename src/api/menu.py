"""Module contains menu API"""
import uuid

from fastapi import APIRouter, HTTPException

from schemas import MenuSchema
from uof.uofs import MenuUOF

router = APIRouter(
    prefix='/menus',
    tags=['Menu CRUD']
)


@router.get('')
async def get_all_menus() -> list:
    """Get all menus"""
    return await MenuUOF.get_all()


@router.get('/{menu_id}')
async def get_menu(menu_id: uuid.UUID) -> dict:
    """Get one menu by id"""
    resp = await MenuUOF.get(menu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')
    return resp


@router.post('', status_code=201)
async def post_menu(menu: MenuSchema) -> dict:
    """Create one menu"""
    return await MenuUOF.create(menu.model_dump())


@router.delete('/{menu_id}')
async def delete_menu(menu_id: uuid.UUID) -> None:
    """Delete one menu"""
    if await MenuUOF.delete(menu_id):
        return
    raise HTTPException(status_code=404, detail='menu not found')


@router.patch('/{menu_id}')
async def update_menu(menu_id: uuid.UUID, menu: MenuSchema) -> dict:
    """Delete one menu"""
    resp = await MenuUOF.update(menu_id, menu.model_dump())
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')
    return resp
