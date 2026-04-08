import asyncio
import logging
import traceback
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.async_log import init_logger
from app.routers import users, admins, accounts, payments
from app.database import get_session, create_database
from os import getenv
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN=getenv('ACCESS_TOKEN')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Параметры приложения."""
    asyncio.create_task(init_logger())
    await create_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title='DimaTech_web',
    version='1.0.1',
)
app.include_router(users.router)
app.include_router(admins.router)
app.include_router(accounts.router)
app.include_router(payments.router)


api_key = APIKeyHeader(name='Authorization')


def check_api_key(authorization: str = Depends(api_key)):
    """Проверка ключа api для openapi"""

    if not authorization or str(authorization) != ACCESS_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorized')
    return True


