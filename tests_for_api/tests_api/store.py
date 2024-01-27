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
        print('Added new item')

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
    menu_id: uuid.UUID | None
    items: [OutputSubmenuSchema] = []
    litem: OutputSubmenuSchema | None

    @classmethod
    def clear(cls):
        cls.items = []
        cls.litem = None
        cls.menu_id = None

class DishStore(AbstractStore):
    items: [OutputDishSchema] = []
    litem: OutputDishSchema | None
    menu_id: uuid.UUID | None
    submenu_id: uuid.UUID | None

    @classmethod
    def clear(cls):
        cls.items = []
        cls.litem = None
        cls.menu_id = None
        cls.submenu_id = None
