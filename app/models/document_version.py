import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
    )

    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    document: Mapped["Document"] = relationship(back_populates="versions")

    from sqlalchemy import Index

    __table_args__ = (
        Index(
            "idx_doc_version_latest",
            document_id,
            version.desc()
        ),
    )