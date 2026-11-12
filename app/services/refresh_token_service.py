import hashlib
import secrets

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.models.refresh_token_family import RefreshTokenFamily
from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS

from sqlalchemy import select, update
from app.models.user import User

class InvalidRefreshToken(Exception):
    pass

class RefreshTokenReuseDetected(Exception):
    pass

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

def create_refresh_token(
        db: Session,
        user_id: UUID
        ) -> str:
    raw_token = generate_refresh_token()

    token_hash = hash_refresh_token(raw_token)
    family = RefreshTokenFamily(
        user_id = user_id 
    )

    db.add(family)
    db.flush()

    refresh_token = RefreshToken(
        family_id = family.id,
        token_hash = token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    db.add(refresh_token)
    return raw_token

def rotate_refresh_token(
        db: Session,
        raw_token: str
):
    token_hash = hash_refresh_token(raw_token)

    token = db.scalar(
       select(RefreshToken).where(
           RefreshToken.token_hash == token_hash
       ).with_for_update()
    )

    #lock token family
    family = db.scalar(
        select(RefreshTokenFamily).where(
            RefreshTokenFamily.id == token.family_id
        ).with_for_update()
    )

    if family is None or family.revoked_at is not None:
        raise InvalidRefreshToken()

    now = datetime.now(timezone.utc)

    if token.revoked_at is not None:
        family.revoked_at = now

        #Revoke all tokens in this family

        db.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family.id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        db.commit()

        raise RefreshTokenReuseDetected()

    if token.expires_at < now:
        raise InvalidRefreshToken()

    #check if user is still active
    user = db.scalar(
        select(User).where(
            User.id == family.user_id 
        )
    )

    if user is None or not user.is_active:
        family.revoked_at = now

        db.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family.id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )

        db.commit()
        raise RefreshTokenReuseDetected()

    #rotate token
    new_token_str = generate_refresh_token()
    new_token = RefreshToken(
        family_id = family.id,
        token_hash = hash_refresh_token(new_token_str),
        expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    db.add(new_token)
    db.flush()

    token.revoked_at=now
    token.replaced_by=new_token.id

    db.commit()

    return user.id, new_token_str

    
   

   