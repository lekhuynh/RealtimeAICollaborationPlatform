import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from sqlalchemy import Index

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
    )

    content: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String, default="text")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    # relationships
    document: Mapped["Document"] = relationship(back_populates="messages")

    __table_args__ = (
        # chat realtime (core query)
        Index(
            "idx_msg_doc_created_desc",
            document_id,
            created_at.desc()
        ),
        Index(
            "idx_msg_cover",
            document_id,
            created_at.desc(),
            postgresql_include=["content", "user_id"]
        )
    )
    