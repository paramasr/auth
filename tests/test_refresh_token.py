from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.services.refresh_token_service import create_refresh_token, hash_refresh_token
from datetime import datetime, timedelta, timezone
from app.core.config import REFRESH_TOKEN_EXPIRE_DAYS
from sqlalchemy import select

def test_refresh_token_expiration(db_session):
    user = User(
        email="alice.example.com",
        password_hash="test-hash"
    )

    db_session.add(user)
    db_session.flush()

    raw_token = create_refresh_token(db_session, user.id)
    db_session.flush()

    stored_token = db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == hash_refresh_token(raw_token)
        )
    )

    expected_expiration = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    difference = abs(stored_token.expires_at - expected_expiration).total_seconds()

    assert difference < 5

