"""Project pydantic schemas"""
import uuid

from pydantic import BaseModel, field_serializer


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

    @field_serializer('id')
    def serialize_id(self, id: uuid.UUID, _info):
        return str(id)

    @field_serializer('submenu_id')
    def serialize_submenu_id(self, submenu_id: uuid.UUID, _info):
        return str(submenu_id)


class ExceptionS(BaseModel):
    detail: str


class SubmenuSchemaAll(OutputSubmenuSchema):
    dishes: list[OutputDishSchema]

    @field_serializer('id')
    def serialize_id(self, id: uuid.UUID, _info):
        return str(id)

    @field_serializer('menu_id')
    def serialize_menu_id(self, menu_id: uuid.UUID, _info):
        return str(menu_id)


class MenuSchemaAll(OutputMenuSchema):
    submenus: list[SubmenuSchemaAll]

    @field_serializer('id')
    def serialize_id(self, id: uuid.UUID, _info):
        return str(id)
