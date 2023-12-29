import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database import get_session
from app.database import metadata
from config import TEST_DB_URL
from app.main import app


client = TestClient(app)


DATABASE_URL_TEST = TEST_DB_URL

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test

async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_session] = get_test_session

@pytest.fixture(autouse=True, scope='session')
def prepare_database():
    asyncio.run(create_table())
    yield
    asyncio.run(drop_table())



async def create_table():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def drop_table():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)