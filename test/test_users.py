import pytest
from unittest.mock import patch, AsyncMock
from app.models.user import User
from app.models.enums import SystemRole
from datetime import datetime

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.users.user_service")
async def test_get_current_user_profile(mock_user_service, client, override_current_user):
    response = await client.get("/api/v1/users/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "user"

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.users.user_service")
async def test_update_current_user(mock_user_service, client, override_current_user, test_user):
    updated_user = User(
        id=test_user.id,
        email="test@example.com",
        full_name="Updated Name",
        role=SystemRole.USER,
        password_hash="hashed_password",
        created_at=datetime.now()
    )
    mock_user_service.update_user = AsyncMock(return_value=updated_user)

    payload = {
        "full_name": "Updated Name"
    }

    response = await client.put("/api/v1/users/me", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
