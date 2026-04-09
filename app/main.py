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
from app.routers import users, admins, accounts, payments, auth, webhook
from app.database import get_session, create_database


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
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admins.router)
app.include_router(accounts.router)
app.include_router(payments.router)
app.include_router(webhook.router)



