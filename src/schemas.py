"""Project pydantic schemas"""
import uuid

from pydantic import BaseModel


class MenuSchema(BaseModel):
    """Menu input schema"""
    title: str
    description: str


class SubmenuSchema(MenuSchema):
    """Submenu input schema"""


class DishSchema(MenuSchema):
    """Dish input schema"""
    price: str


class OutputMenuSchema(MenuSchema):
    """Menu output schema"""
    id: uuid.UUID
    submenus_count: int
    dishes_count: int


class OutputSubmenuSchema(SubmenuSchema):
    """Submenu output schema"""
    id: uuid.UUID
    dishes_count: int
    menu_id: uuid.UUID


class OutputDishSchema(DishSchema):
    """Dish output schema"""
    id: uuid.UUID
    submenu_id: uuid.UUID


class ExceptionS(BaseModel):
    detail: str
