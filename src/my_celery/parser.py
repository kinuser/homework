from typing import List

import requests as rs
import csv
from celery import Celery
from my_celery.schemas import MenuSchemaTable, SubmenuSchemaTable, DishSchemaTable
from uuid import UUID
from uof.uofs import AllUOF
import asyncio



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
            result['price'] = arr[3]
            return result
        return None
    except Exception as e:
        return None


def parse():
    with open('sheet.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        menus_list: List[MenuSchemaTable] = []
        submenus_list: List[SubmenuSchemaTable] = []
        dishes_list: List[DishSchemaTable] = []
        cur_menu_id = None | UUID
        cur_submenu_id = None | UUID
        for row in reader:
            print('1')
            if str_parser(row[0:3], 'menu'):
                menu = MenuSchemaTable(
                    **str_parser(row[0:3], 'menu')
                )
                menus_list.append(menu)
                cur_menu_id = menu.id
            elif str_parser(row[1:4], 'submenu'):
                submenu = SubmenuSchemaTable(
                    menu_id=cur_menu_id,
                    **str_parser(row[1:4], 'submenu')
                )
                cur_submenu_id=submenu.id
                submenus_list.append(submenu)
            elif str_parser(row[2:6], 'dish'):
                dish = DishSchemaTable(
                    submenu_id=cur_submenu_id,
                    **str_parser(row[2:6], 'dish')
                )
                dishes_list.append(dish)

        return menus_list, submenus_list, dishes_list


app = Celery(
    'my_celery.parser',
    broker='amqp://guest:guest@localhost:5672',
    backend='redis://localhost:6379/0'
)

app.loop = asyncio.get_event_loop()


async def run_synchro():
    await AllUOF.synchronize_gsheet(*parse())


@app.task
def get_and_parse():
    resp = rs.get(
        'https://docs.google.com/spreadsheets/d/15YH38QEUAewpRDowJduQHrQVM-XGolw1JMyTvjehN_U'
        '/export?format=csv'
    )
    with open('sheet.csv', 'w+') as f:
        f.write(resp.content.decode())
    app.loop.run_until_complete(run_synchro())

    get_and_parse.apply_async(countdown=15)
