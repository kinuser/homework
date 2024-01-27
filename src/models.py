import uuid
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

Base = declarative_base()


class MenuOrm(Base):
    __tablename__ = 'menu'
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    description: Mapped[str]
    title: Mapped[str]
    submenu: Mapped[List["SubmenuOrm"]] = relationship(cascade="all, delete-orphan", lazy='joined')

    def to_read_model(self) -> dict:
        return {
            'id': self.id,
            'description': self.description,
            'title': self.title,
            'submenu': [x.to_read_model() for x in self.submenu]
        }


class SubmenuOrm(Base):
    __tablename__ = 'submenu'
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    description: Mapped[str]
    title: Mapped[str]
    menu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('menu.id', ondelete='CASCADE'))
    dish: Mapped[List["DishOrm"]] = relationship(cascade="all, delete-orphan", lazy='joined')

    def to_read_model(self) -> dict:
        return {
            'id': self.id,
            'description': self.description,
            'title': self.title,
            'menu_id': self.menu_id,
            'dish': [x.to_read_model() for x in self.dish]
        }


class DishOrm(Base):
    __tablename__ = 'dish'
    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    description: Mapped[str]
    title: Mapped[str]
    price: Mapped[str]
    submenu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('submenu.id', ondelete='CASCADE'))

    def to_read_model(self) -> dict:
        return {
            'id': self.id,
            'description': self.description,
            'title': self.title,
            'price': self.price,
            'submenu_id': self.submenu_id
        }

