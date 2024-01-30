from fastapi import FastAPI
from api.router import main_router as router
from contextlib import asynccontextmanager
from database import async_engine
from models import metadata
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield
    # Clean up the ML models and release the resources
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)