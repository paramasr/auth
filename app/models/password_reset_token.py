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

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id:Mapped[uuid:Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4 
    )

    user_id:Mapped[uuid:Uuid] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id"),
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

    used_at:Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    revoked_at:Mapped[datetime | None] = mapped_column(
            DateTime(timezone=True),
            nullable=True
        )

    