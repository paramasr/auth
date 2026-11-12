import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Uuid,
    String,
    ForeignKey,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id:Mapped[uuid:Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4 
    )

    family_id:Mapped[uuid:Uuid] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("refresh_token_families.id"),
        index=True,
        nullable=False
    )

    token_hash:Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )

    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )

    expires_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    revoked_at:Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    replaced_by:Mapped[uuid:Uuid | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("refresh_tokens.id"),
        nullable=True
    )