"""Store for client environments"""
import uuid
from abc import ABC
from typing import Any

from tests.test_schemas import OutputDishSchema, OutputMenuSchema, OutputSubmenuSchema


class AbstractStore(ABC):
    """After delete_last litem becomes empty"""
    items: Any
    litem: Any

    @classmethod
    def add_item(cls, menu) -> None:
        """Add item to store"""
        cls.items.append(menu)
        cls.litem = cls.items[-1]
        print('Added new item')

    @classmethod
    def delete_last(cls) -> None:
        """Delete item from store"""
        cls.litem = None
        del cls.items[-1]

    @classmethod
    def update(cls, menu) -> None:
        """Update last item"""
        cls.items[-1] = menu
        cls.litem = None


class MenuStore(AbstractStore):
    """Class for menu variables"""
    items: list[OutputMenuSchema | None] = []
    litem: OutputMenuSchema | None


class SubmenuStore(AbstractStore):
    """Class for submenu variables"""
    menu_id: uuid.UUID | None
    items: list[OutputSubmenuSchema | None] = []
    litem: OutputSubmenuSchema | None

    @classmethod
    def clear(cls):
        """Clear all store"""
        cls.items = []
        cls.litem = None
        cls.menu_id = None


class DishStore(AbstractStore):
    """Class for dish variables"""
    items: list[OutputDishSchema | None] = []
    litem: OutputDishSchema | None
    menu_id: uuid.UUID | None
    submenu_id: uuid.UUID | None

    @classmethod
    def clear(cls):
        """Clear all store"""
        cls.items = []
        cls.litem = None
        cls.menu_id = None
        cls.submenu_id = None
