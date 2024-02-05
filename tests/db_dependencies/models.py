"""DB models"""
import uuid

from sqlalchemy import UUID, Column, ForeignKey, MetaData, String, Table

metadata = MetaData()

menu_table = Table(
    'menu',
    metadata,
    Column('id', UUID, primary_key=True, default=uuid.uuid4),
    Column('title', String),
    Column('description', String),
)

submenu_table = Table(
    'submenu',
    metadata,
    Column('id', UUID, primary_key=True, default=uuid.uuid4),
    Column('title', String),
    Column('description', String),
    Column('menu_id', UUID, ForeignKey('menu.id', ondelete='CASCADE')),
)

dish_table = Table(
    'dish',
    metadata,
    Column('id', UUID, primary_key=True, default=uuid.uuid4),
    Column('title', String),
    Column('description', String),
    Column('price', String),
    Column('submenu_id', UUID, ForeignKey('submenu.id', ondelete='CASCADE'))
)
