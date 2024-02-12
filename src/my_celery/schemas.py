"""Project pydantic schemas"""
from typing import List

from pydantic import BaseModel
from uuid import UUID


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
