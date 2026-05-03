import pytest
import asyncio
from httpx import AsyncClient
from typing import AsyncGenerator
from unittest.mock import AsyncMock
import uuid

from app.main import app
from app.db.session import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.models.enums import SystemRole

# Fixture required for pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

async def override_get_db():
    mock_session = AsyncMock()
    yield mock_session

app.dependency_overrides[get_db] = override_get_db

from datetime import datetime

@pytest.fixture
def test_user():
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        role=SystemRole.USER,
        password_hash="hashed_password",
        created_at=datetime.now()
    )
    return user

@pytest.fixture
def override_current_user(test_user):
    async def _override():
        return test_user
    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.pop(get_current_user, None)

import pytest_asyncio

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
