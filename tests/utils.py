from uuid import UUID

from fastapi_mock.main import app
from test_config import APP_HOST, APP_PORT


def reverse(
        case: str,
        menu_id: UUID | None = None,
        submenu_id: UUID | None = None,
        dish_id: UUID | None = None
) -> str:
    path = f'http://{APP_HOST}:{APP_PORT}'
    try:
        if menu_id and submenu_id and dish_id:
            return path + app.url_path_for(case, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        if menu_id and submenu_id:
            return path + app.url_path_for(case, menu_id=menu_id, submenu_id=submenu_id)
        if menu_id:
            return path + app.url_path_for(case, menu_id=menu_id)
        return path + app.url_path_for(case)
    except Exception as e:
        print(e)
        return ''
