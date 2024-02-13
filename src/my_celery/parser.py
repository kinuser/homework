import asyncio
import csv
from uuid import UUID

import requests as rs
from celery import Celery

from config import RAB_HOST, RAB_PORT, RED_HOST, RED_PORT, SHEET_URL
from my_celery.schemas import DishSchemaTable, MenuSchemaTable, SubmenuSchemaTable
from uof.uofs import AllUOF


def str_parser(arr: list, str_type: str) -> dict | None:
    """Parse a csv row into dict"""
    try:
        result = {'id': UUID(arr[0]), 'title': arr[1], 'description': arr[2]}
        if str_type == 'menu':
            result['submenus'] = []
            return result
        elif str_type == 'submenu':
            result['dishes'] = []
            return result
        elif str_type == 'dish':
            if len(arr) == 5:
                result['price'] = str(round(float(arr[3]) * (1 - float('0.' + arr[4].replace('%', ''))), 2))
            else:
                result['price'] = arr[3]
            return result
        return None
    except Exception as e:
        return None


def parse() -> tuple[list[MenuSchemaTable], list[SubmenuSchemaTable], list[DishSchemaTable]]:
    with open('sheet.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        menus_list: list[MenuSchemaTable] = []
        submenus_list: list[SubmenuSchemaTable] = []
        dishes_list: list[DishSchemaTable] = []
        # cur_menu_id: UUID | None
        # cur_submenu_id: UUID | None
        for row in reader:
            print(row)
            m_true = str_parser(row[0:3], 'menu')
            sm_true = str_parser(row[1:4], 'submenu')
            d_true = str_parser(row[2:7], 'dish')
            if m_true:
                menu = MenuSchemaTable(
                    **m_true
                )
                menus_list.append(menu)
                cur_menu_id: UUID = menu.id
            elif sm_true:
                submenu = SubmenuSchemaTable(
                    menu_id=cur_menu_id,
                    **sm_true
                )
                cur_submenu_id: UUID = submenu.id
                submenus_list.append(submenu)
            elif d_true:
                dish = DishSchemaTable(
                    submenu_id=cur_submenu_id,
                    **d_true
                )
                dishes_list.append(dish)

        return menus_list, submenus_list, dishes_list


app = Celery(
    'my_celery.parser',
    broker=f'amqp://guest:guest@{RAB_HOST}:{RAB_PORT}',
    backend=f'redis://{RED_HOST}:{RED_PORT}/0'
)

app.loop = asyncio.get_event_loop()


async def run_synchro():
    await AllUOF.synchronize_gsheet(*parse())


@app.task
def get_and_parse():
    resp = rs.get(
        SHEET_URL + '/export?format=csv'
    )
    with open('sheet.csv', 'w+') as f:
        f.write(resp.content.decode())
    app.loop.run_until_complete(run_synchro())

    get_and_parse.apply_async(countdown=15)
