import uuid

from pydantic import BaseModel


class MenuSchema(BaseModel):
    title: str
    description: str


class SubmenuSchema(MenuSchema):
    pass


class DishSchema(MenuSchema):
    price: str


class OutputMenuSchema(MenuSchema):
    id: uuid.UUID
    submenus_count: int
    dishes_count: int


class OutputSubmenuSchema(SubmenuSchema):
    id: uuid.UUID
    dishes_count: int
    menu_id: uuid.UUID


class OutputDishSchema(MenuSchema):
    id: uuid.UUID
    price: str
    submenu_id: uuid.UUID
