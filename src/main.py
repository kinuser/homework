"""Main startup file"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

import redis
import uvicorn
from fastapi import FastAPI

from api.router import main_router as router
from config import RED_HOST, RED_PORT
from database import async_engine
from models import metadata
from my_celery.parser import get_and_parse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Routine before startup and after shutdown"""
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    if RED_HOST and RED_PORT:
        c = redis.Redis(host=RED_HOST, port=int(RED_PORT), decode_responses=True)
        c.json().set('menus', '$', [])
        get_and_parse.apply_async(countdown=60)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
