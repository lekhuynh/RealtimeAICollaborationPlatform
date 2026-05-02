import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, Enum as SQLEnum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SystemRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String)

    role: Mapped[SystemRole] = mapped_column(
        SQLEnum(SystemRole, name="system_role"),
        default=SystemRole.USER,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("now()")
    )

    # relationships
    documents_owned: Mapped[List["Document"]] = relationship(
        back_populates="owner"
    )

    memberships: Mapped[List["DocumentMember"]] = relationship(
        back_populates="user"
    )