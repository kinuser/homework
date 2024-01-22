from pydantic import BaseModel


class MenuSchema(BaseModel):
    title: str
    description: str


class SubmenuSchema(MenuSchema):
    pass


class DishSchema(MenuSchema):
    price: str
