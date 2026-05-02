import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Text, DateTime, ForeignKey, text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text)

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    # relationships
    owner: Mapped["User"] = relationship(back_populates="documents_owned")

    members: Mapped[List["DocumentMember"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )

    messages: Mapped[List["Message"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )

    versions: Mapped[List["DocumentVersion"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        # load document theo owner
        Index(
            "idx_doc_owner_created",
            owner_id,
            created_at.desc()
        ),
    )