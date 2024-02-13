"""Project pydantic schemas"""
from uuid import UUID

from pydantic import BaseModel


class DishSchemaTable(BaseModel):
    """Dish input schema"""
    id: UUID
    submenu_id: UUID
    title: str
    description: str
    price: str


class SubmenuSchemaTable(BaseModel):
    """Submenu input schema"""
    id: UUID
    menu_id: UUID
    title: str
    description: str


class MenuSchemaTable(BaseModel):
    """Menu input schema"""
    id: UUID
    title: str
    description: str
