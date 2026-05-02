import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIRequest(Base):
    __tablename__ = "ai_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id"),
    )

    type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    from sqlalchemy import Index, text

    __table_args__ = (
        # worker queue (cực quan trọng)
        Index(
            "idx_ai_pending_created",
            "status",
            "created_at",
            postgresql_where=text("status = 'pending'")
        ),
    )