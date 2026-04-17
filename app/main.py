from fastapi import FastAPI
from app.seed import seed_data, upload_products
from contextlib import asynccontextmanager
from app.api import route
from app.database import init_chat_table

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_chat_table()
    seed_data()
    upload_products()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(route)



