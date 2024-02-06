"""Module contains submenu API"""
from uuid import UUID

from fastapi import APIRouter, HTTPException

from schemas import ExceptionS, OutputSubmenuSchema, SubmenuSchema
from uof.uofs import SubmenuUOF

router = APIRouter(
    prefix='/menus',
    tags=['Submenu CRUD']
)

PARENT = '/{menu_id}/submenus'


@router.get(
    PARENT,
    response_model=list[OutputSubmenuSchema],
    tags=['get']
)
async def get_all_submenus(menu_id: UUID) -> list[OutputSubmenuSchema]:
    """Get all submenus"""
    return await SubmenuUOF.get_all(menu_id)


@router.get(
    PARENT + '/{submenu_id}',
    response_model=OutputSubmenuSchema,
    responses={404: {'model': ExceptionS}},
    tags=['get']
)
async def get_submenu(menu_id: UUID, submenu_id: UUID) -> OutputSubmenuSchema:
    """Get one submenu by id"""
    resp = await SubmenuUOF.get(menu_id, submenu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='submenu not found')
    return resp


@router.post(
    PARENT,
    status_code=201,
    response_model=OutputSubmenuSchema,
    responses={404: {'model': ExceptionS}},
    tags=['post']
)
async def post_submenu(menu_id: UUID, submenu: SubmenuSchema) -> OutputSubmenuSchema:
    """Create one submenu"""
    resp = await SubmenuUOF.create(menu_id, submenu)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')
    return resp


@router.delete(
    PARENT + '/{submenu_id}',
    responses={404: {'model': ExceptionS}},
    tags=['delete']
)
async def delete_submenu(menu_id: UUID, submenu_id: UUID) -> None:
    """Delete one submenu"""
    if await SubmenuUOF.delete(menu_id, submenu_id):
        return
    raise HTTPException(status_code=404, detail='submenu not found')


@router.patch(
    PARENT + '/{submenu_id}',
    response_model=OutputSubmenuSchema,
    responses={404: {'model': ExceptionS}},
    tags=['patch']
)
async def update_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuSchema) -> OutputSubmenuSchema:
    """Delete one submenu"""
    resp = await SubmenuUOF.update(menu_id, submenu_id, submenu)
    if not resp:
        raise HTTPException(status_code=404, detail='submenu not found')
    return resp
