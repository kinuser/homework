"""Module contains menu API"""
import uuid

from fastapi import APIRouter, HTTPException

from schemas import ExceptionS, MenuSchema, OutputMenuSchema
from uof.uofs import AllUOF, MenuUOF

router = APIRouter(
    prefix='/menus',
    tags=['Menu CRUD']
)


@router.get(
    '',
    response_model=list[OutputMenuSchema],
    tags=['get']
)
async def get_all_menus() -> list[OutputMenuSchema]:
    """Get all menus"""
    return await MenuUOF.get_all()


@router.get(
    '/{menu_id}',
    response_model=OutputMenuSchema,
    responses={404: {'model': ExceptionS}},
    tags=['get']
)
async def get_menu(menu_id: uuid.UUID) -> OutputMenuSchema:
    """Get one menu by id"""
    resp = await MenuUOF.get(menu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')
    return resp


@router.post(
    '',
    status_code=201,
    response_model=OutputMenuSchema,
    tags=['post']
)
async def post_menu(menu: MenuSchema) -> OutputMenuSchema:
    """Create one menu"""
    return await MenuUOF.create(menu)


@router.delete(
    '/{menu_id}',
    responses={404: {'model': ExceptionS}},
    tags=['delete']
)
async def delete_menu(menu_id: uuid.UUID) -> None:
    """Delete one menu"""
    if await MenuUOF.delete(menu_id):
        return
    raise HTTPException(status_code=404, detail='menu not found')


@router.patch(
    '/{menu_id}',
    response_model=OutputMenuSchema,
    responses={404: {'model': ExceptionS}},
    tags=['patch']
)
async def update_menu(menu_id: uuid.UUID, menu: MenuSchema) -> OutputMenuSchema:
    """Delete one menu"""
    resp = await MenuUOF.update(menu_id, menu)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')
    return resp
