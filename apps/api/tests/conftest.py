"""
Axorks OS Test Fixtures
"""

import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.core.config import get_settings
from src.core.database import get_db
from src.main import app
from src.shared.base_model import Base

settings = get_settings()

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated client with org context (re-login after org creation)."""
    email = "dev-test@axorks.com"
    password = "Password123456!"

    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Dev",
            "last_name": "Tester",
        },
    )

    reg_token = (
        await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    ).json()["data"]["access_token"]

    await client.post(
        "/api/v1/organizations",
        json={"name": "Dev Test Org", "slug": "dev-test-org"},
        headers={"Authorization": f"Bearer {reg_token}"},
    )

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login.json()["data"]["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
