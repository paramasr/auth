import hashlib
import secrets

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken
from app.core.config import PASSWORD_RESET_TOKEN_EXPIRE_MINUTES

from sqlalchemy import select, update
from app.models.user import User


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def hash_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

def create_password_reset_token(
        db: Session,
        user_id: UUID
        ) -> str:
    raw_token = generate_reset_token()

    token_hash = hash_reset_token(raw_token)


    reset_token = PasswordResetToken(
        user_id = str(user_id),
        token_hash = token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    )

    db.add(reset_token)

    return raw_token


def request_password_reset(
        db:Session,
        email: str) -> str | None:

    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User)
        .where(User.email == normalized_email)
        .with_for_update()
    )

    if user is None:
        return None
    now = datetime.now(timezone.utc)

    #revoked existing reset tokens
    db.execute(
        update(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id and
            PasswordResetToken.revoked_at is None and 
            PasswordResetToken.used_at is None
        ).values(revoked_at=now)
    )

    #generate new reset token
    reset_token = create_password_reset_token(db, user.id)
    return reset_token
