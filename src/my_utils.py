from repositories.redis_repos import get_c
from uof.uofs import AllUOF


async def invalidate_cache():
    """Invalidate all cache"""
    c = get_c()
    resp = await AllUOF.get_everything()
    await c.json().set('menus', '$', [x.model_dump() for x in resp])
