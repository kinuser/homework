from uuid import UUID
from fastapi import APIRouter, HTTPException
from database import Session
from models import SubmenuOrm
from repositories.submenu import SubmenuRepository
from schemas import SubmenuSchema

router = APIRouter(
    prefix='/menus',
    tags=['Submenu CRUD']
)

submenu_repo = SubmenuRepository(SubmenuOrm, Session)

perm_string = '/{menu_id}/submenus'


@router.get(perm_string)
async def get_all_submenus(menu_id: UUID):
    resp = await submenu_repo.get_all(menu_id)
    return submenu_repo.to_repr_all(resp)


@router.get(perm_string + '/{submenu_id}')
async def get_submenu(menu_id: UUID, submenu_id: UUID):
    resp = await submenu_repo.get_one(submenu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='submenu not found')

    return submenu_repo.to_repr_one(resp)


@router.post(perm_string, status_code=201)
async def post_submenu(menu_id: UUID, submenu: SubmenuSchema):
    resp = await submenu_repo.create_one(submenu, menu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='submenu not found')
    return submenu_repo.to_repr_one(resp)


@router.delete(perm_string + '/{submenu_id}')
async def delete_submenu(menu_id: UUID, submenu_id: UUID):
    await submenu_repo.delete_one(submenu_id)


@router.patch(perm_string + '/{submenu_id}')
async def update_submenu(menu_id: UUID, submenu_id: UUID, submenu: SubmenuSchema):
    resp = await submenu_repo.update_one(submenu, menu_id, submenu_id)
    if not resp:
        raise HTTPException(status_code=404, detail='menu not found')

    return submenu_repo.to_repr_one(resp)
