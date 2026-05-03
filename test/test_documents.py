import pytest
from unittest.mock import patch, AsyncMock
import uuid
from app.models.document import Document
from app.models.document_member import DocumentMember
from app.models.enums import DocumentRole
from datetime import datetime

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.documents.document_service")
async def test_create_document(mock_doc_service, client, override_current_user, test_user):
    mock_doc = Document(
        id=uuid.uuid4(),
        title="Test Doc",
        content="Hello World",
        owner_id=test_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_doc_service.create_document = AsyncMock(return_value=mock_doc)

    payload = {
        "title": "Test Doc",
        "content": "Hello World"
    }

    response = await client.post("/api/v1/documents/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Doc"
    assert data["owner_id"] == str(test_user.id)

from fastapi import HTTPException
from unittest.mock import MagicMock
from app.main import app
from app.db.session import get_db

@pytest.mark.asyncio
async def test_get_document_forbidden(client, override_current_user):
    old_db = app.dependency_overrides.get(get_db)
    
    async def override_db():
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        yield mock_session
        
    app.dependency_overrides[get_db] = override_db

    doc_id = uuid.uuid4()
    response = await client.get(f"/api/v1/documents/{doc_id}")
    
    app.dependency_overrides[get_db] = old_db
    
    assert response.status_code == 403
    assert "mời" in response.json()["detail"].lower()

@pytest.mark.asyncio
@patch("app.api.v1.endpoints.documents.document_service")
async def test_get_document_success(mock_doc_service, client, override_current_user, test_user):
    doc_id = uuid.uuid4()
    
    mock_member = DocumentMember(
        id=uuid.uuid4(),
        document_id=doc_id,
        user_id=test_user.id,
        role=DocumentRole.OWNER
    )
    
    old_db = app.dependency_overrides.get(get_db)
    async def override_db():
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = mock_member
        mock_session.execute = AsyncMock(return_value=mock_result)
        yield mock_session
        
    app.dependency_overrides[get_db] = override_db

    mock_doc = Document(
        id=doc_id,
        title="My Document",
        content="Content",
        owner_id=test_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    mock_doc_service.get_document = AsyncMock(return_value=mock_doc)

    response = await client.get(f"/api/v1/documents/{doc_id}")
    
    app.dependency_overrides[get_db] = old_db
    
    assert response.status_code == 200
    assert response.json()["title"] == "My Document"
