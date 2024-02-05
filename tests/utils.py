from uuid import UUID

from test_config import APP_HOST, APP_PORT


def reverse(case: str, m_id: UUID | None = None, sm_id: UUID | None = None, d_id: UUID | None = None):
    """Django reverse analog for tests"""

    path = f'http://{APP_HOST}:{APP_PORT}/api/v1/menus'

    if case == 'menu':
        if m_id is not None:
            return path + '/' + str(m_id)
        return path

    if case == 'submenu':
        if m_id is None:
            raise Exception('Menu id is none')
        path = f'{path}/{str(m_id)}/submenus'
        if sm_id is not None:
            return path + '/' + str(sm_id)
        return path

    if case == 'dish':
        if m_id is None or sm_id is None:
            raise Exception('Menu or submenu id is none')
        path = f'{path}/{str(m_id)}/submenus/{sm_id}/dishes'
        if d_id is not None:
            return path + '/' + str(d_id)
        return path
    raise Exception('Invalid argiments')
