import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import DocumentRole
from sqlalchemy import Index, UniqueConstraint


class DocumentMember(Base):
    __tablename__ = "document_members"

    __table_args__ = (
        UniqueConstraint("document_id", "user_id", name="uq_doc_user"),
    )

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
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    role: Mapped[DocumentRole] = mapped_column(
        SQLEnum(DocumentRole, name="document_role"),
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="memberships")
    document: Mapped["Document"] = relationship(back_populates="members")


    __table_args__ = (
        # check permission (critical)
        UniqueConstraint("document_id", "user_id", name="uq_doc_user"),

        # list members
        Index("idx_member_doc", "document_id"),
    )