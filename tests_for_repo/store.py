import uuid
from abc import ABC
from typing import Any

from schemas import OutputMenuSchema, OutputSubmenuSchema, OutputDishSchema


class AbstractStore(ABC):
    """After delete_last litem becomes empty"""
    items: Any
    litem: Any
    @classmethod
    def add_item(cls, menu) -> None:
        cls.items.append(menu)
        cls.litem = cls.items[-1]

    @classmethod
    def delete_last(cls) -> None:
        cls.litem = None
        del cls.items[-1]

    @classmethod
    def update(cls, menu) -> None:
        cls.items[-1] = menu
        cls.litem = None


class MenuStore(AbstractStore):
    items: [OutputMenuSchema] = []
    litem: OutputMenuSchema | None


class SubmenuStore(AbstractStore):
    menu_id: uuid.UUID
    items: [OutputSubmenuSchema] = []
    litem: OutputSubmenuSchema | None


class DishStore(AbstractStore):
    items: [OutputDishSchema] = []
    litem: OutputDishSchema | None
    menu_id: uuid.UUID
    submenu_id: uuid.UUID

    @classmethod
    def clear(cls):
        del cls.items
        del cls.litem
        del cls.menu_id
        del cls.submenu_id


