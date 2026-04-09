import asyncio

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine
)
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from os import getenv
from dotenv import load_dotenv


load_dotenv()


# NOTE: postgres db params

POSTGRES_DB = getenv('POSTGRES_DB')
POSTGRES_USER = getenv('POSTGRES_USER')
POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = getenv('POSTGRES_HOST')
POSTGRES_PORT = int(getenv('POSTGRES_PORT', 5432))

Base = declarative_base()



dsn = (f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
       f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')


engine = create_async_engine(dsn, echo=False, future=True, pool_size=100)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def create_database() -> None:
    """Create tables."""

    async with engine.begin() as db_engine:
        # await db_engine.run_sync(Base.metadata.drop_all) #Строка для пересоздания таблиц
        await db_engine.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get assync db session."""

    async with async_session() as session:
        yield session
