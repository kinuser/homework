"""Module contains menu API"""
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from database import Session
from my_utils import invalidate_cache
from repositories.menu import MenuRepository
from schemas import ExceptionS, MenuSchema, OutputMenuSchema
from uof.uofs import MenuUOF

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
async def post_menu(menu: MenuSchema, background_task: BackgroundTasks) -> OutputMenuSchema:
    """Create one menu"""
    async with Session() as s:
        r = MenuRepository(s)
        db_r = await r.create_one(menu)
        if db_r:
            await s.commit()
            background_task.add_task(invalidate_cache)
            return db_r
        raise Exception('Error, something went wrong')


@router.delete(
    '/{menu_id}',
    responses={404: {'model': ExceptionS}},
    tags=['delete']
)
async def delete_menu(menu_id: uuid.UUID, background_task: BackgroundTasks) -> None:
    """Delete one menu"""
    async with Session() as s:
        r = MenuRepository(s)
        if await r.delete_one(menu_id):
            await s.commit()
            background_task.add_task(invalidate_cache)
        else:
            raise HTTPException(status_code=404, detail='menu not found')


@router.patch(
    '/{menu_id}',
    response_model=OutputMenuSchema,
    responses={404: {'model': ExceptionS}},
    tags=['patch']
)
async def update_menu(menu_id: uuid.UUID, menu: MenuSchema, background_task: BackgroundTasks) -> OutputMenuSchema:
    """Delete one menu"""
    async with Session() as s:
        r = MenuRepository(s)
        db_r = await r.update_one(menu_id, menu)
        if db_r:
            await s.commit()
            background_task.add_task(invalidate_cache)
            return db_r
        raise Exception('Error, something went wrong')
