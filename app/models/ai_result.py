import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIResult(Base):
    __tablename__ = "ai_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_requests.id", ondelete="CASCADE"),
    )

    result: Mapped[str] = mapped_column(Text)
    scope: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    from sqlalchemy import Index

    __table_args__ = (
        Index("idx_ai_result_request", "request_id"),
    )