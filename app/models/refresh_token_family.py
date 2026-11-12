import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Uuid,
    ForeignKey,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RefreshTokenFamily(Base):
    __tablename__ = "refresh_token_families"

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

    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False
    )

    revoked_at:Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    