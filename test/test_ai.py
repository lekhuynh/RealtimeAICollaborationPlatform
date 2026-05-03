import pytest
from unittest.mock import patch, AsyncMock
import uuid
from app.models.ai_request import AIRequest
from app.models.enums import SystemRole
from datetime import datetime

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.ai.document_member_service")
@patch("app.api.v1.endpoints.ai.ai_service")
async def test_create_ai_request_forbidden(mock_ai_service, mock_member_service, client, override_current_user):
    # Simulates user not having access to document
    mock_member_service.check_user_role = AsyncMock(return_value=None)

    payload = {
        "document_id": str(uuid.uuid4()),
        "type": "summarize"
    }

    response = await client.post("/api/v1/ai/request", json=payload)
    
    assert response.status_code == 403
    assert "permissions" in response.json()["detail"].lower()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.ai.document_member_service")
@patch("app.api.v1.endpoints.ai.ai_service")
async def test_create_ai_request_success(mock_ai_service, mock_member_service, client, override_current_user, test_user):
    # Setup access
    mock_member_service.check_user_role = AsyncMock(return_value="owner")
    
    doc_id = uuid.uuid4()
    req_id = uuid.uuid4()
    
    # Mock AI response
    mock_request = AIRequest(
        id=req_id,
        document_id=doc_id,
        type="summarize",
        status="pending",
        user_id=test_user.id,
        created_at=datetime.now()
    )
    mock_ai_service.create_request = AsyncMock(return_value=mock_request)

    payload = {
        "document_id": str(doc_id),
        "type": "summarize"
    }

    response = await client.post("/api/v1/ai/request", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "summarize"
    assert data["status"] == "pending"
