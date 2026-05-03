import pytest
from unittest.mock import patch, AsyncMock
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.enums import SystemRole
import uuid
from datetime import datetime

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.auth.user_service")
async def test_register_success(mock_user_service, client):
    # Setup mock
    mock_user = User(
        id=uuid.uuid4(),
        email="newuser@example.com",
        full_name="New User",
        role=SystemRole.USER,
        password_hash="hashed",
        created_at=datetime.now()
    )
    mock_user_service.get_user_by_email = AsyncMock(return_value=None)
    mock_user_service.create_user = AsyncMock(return_value=mock_user)

    payload = {
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    }

    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.auth.user_service")
async def test_register_existing_email(mock_user_service, client):
    # Setup mock
    mock_user_service.get_user_by_email = AsyncMock(return_value=True) # user exists

    payload = {
        "email": "existing@example.com",
        "password": "password123",
        "full_name": "Existing User"
    }

    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.auth.verify_password")
@patch("app.api.v1.endpoints.auth.user_service")
async def test_login_success(mock_user_service, mock_verify, client):
    mock_user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test",
        role=SystemRole.USER,
        password_hash="hashed",
        created_at=datetime.now()
    )
    mock_user_service.get_user_by_email = AsyncMock(return_value=mock_user)
    mock_verify.return_value = True

    payload = {
        "username": "test@example.com",
        "password": "password123"
    }

    # Use data= for form data (OAuth2PasswordRequestForm expects form-urlencoded)
    response = await client.post("/api/v1/auth/login", data=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
