import uuid
from sqlalchemy import Table, Column, MetaData, String, Integer, ForeignKey, Numeric, UUID, DDL, event, select, func

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


def get_all_menus():
    sub_without_id = (
        select(func.count(submenu_table.c.id).label('submenus_count'), submenu_table.c.menu_id)
        .group_by(submenu_table.c.menu_id)
        .cte()
    )
    subs_with_id = (
        select(sub_without_id.c.submenus_count, sub_without_id.c.menu_id, submenu_table.c.id)
        .outerjoin(sub_without_id, sub_without_id.c.menu_id == submenu_table.c.menu_id)
        .cte()
    )
    dish_c = (
        select(func.count(dish_table.c.id).label('dishes_count'), dish_table.c.submenu_id, )
        .group_by(dish_table.c.submenu_id)
        .cte()
    )

    counters = (
        select(
            func.sum(dish_c.c.dishes_count).label('dishes_count'),
            func.count(subs_with_id.c.submenus_count).label('submenus_count'),
            subs_with_id.c.menu_id
        )
        .outerjoin(dish_c, subs_with_id.c.id == dish_c.c.submenu_id)
        .group_by(subs_with_id.c.menu_id)
        .cte()
    )

    get_all_menu = (
        select(menu_table,
               func.coalesce(counters.c.dishes_count, 0).label('dishes_count'),
               func.coalesce(counters.c.submenus_count, 0).label('submenus_count'))
        .distinct()
        .outerjoin_from(menu_table, counters, menu_table.c.id == counters.c.menu_id)

    )

    return get_all_menu


def get_one_menu(id: UUID):
    sub_without_id = (
        select(func.count(submenu_table.c.id).label('submenus_count'), submenu_table.c.menu_id)
        .group_by(submenu_table.c.menu_id)
        .cte()
    )
    subs_with_id = (
        select(sub_without_id.c.submenus_count, sub_without_id.c.menu_id, submenu_table.c.id)
        .outerjoin(sub_without_id, sub_without_id.c.menu_id == submenu_table.c.menu_id)
        .cte()
    )
    dish_c = (
        select(func.count(dish_table.c.id).label('dishes_count'), dish_table.c.submenu_id, )
        .group_by(dish_table.c.submenu_id)
        .cte()
    )

    counters = (
        select(
            func.sum(dish_c.c.dishes_count).label('dishes_count'),
            func.count(subs_with_id.c.submenus_count).label('submenus_count'),
            subs_with_id.c.menu_id
        )
        .outerjoin(dish_c, subs_with_id.c.id == dish_c.c.submenu_id)
        .group_by(subs_with_id.c.menu_id)
        .cte()
    )

    get_one = (
        select(menu_table,
               func.coalesce(counters.c.dishes_count, 0).label('dishes_count'),
               func.coalesce(counters.c.submenus_count, 0).label('submenus_count'))
        .distinct()
        .where(menu_table.c.id == id )
        .outerjoin_from(menu_table, counters, menu_table.c.id == counters.c.menu_id)

    )

    return get_one


def get_all_submenus(id: UUID):
    query = (
                select(submenu_table, func.count(dish_table.c.id).label('dishes_count'))
                .where(submenu_table.c.menu_id == id)
                .outerjoin(dish_table, dish_table.c.submenu_id==submenu_table.c.id)
                .group_by(submenu_table.c.id)
            )
    return query


def get_one_submenu(id: UUID):
    query = (
        select(submenu_table, func.count(dish_table.c.id).label('dishes_count'))
        .where(submenu_table.c.id == id)
        .outerjoin(dish_table, dish_table.c.submenu_id == submenu_table.c.id)
        .group_by(submenu_table.c.id)
    )
    return query
