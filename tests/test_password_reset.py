from uuid import uuid4

from sqlalchemy import select

from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.services.password_reset_service import (
    create_password_reset_token,
    hash_reset_token
)

def test_create_password_reset_token(db_session):
    user=User(
            email="alice@example.com",
            password_hash="test-hash"
    )

    db_session.add(user)
    db_session.flush()

    raw_token = create_password_reset_token(db_session, user.id)

    db_session.flush()

    expected_hash = hash_reset_token(raw_token)

    stored_token = db_session.scalar(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user.id)
    )

    assert expected_hash == stored_token.token_hash

def test_password_reset_existing_user(client):
    signup_response = client.post(
            "/auth/signup",
            json={
                "email":"alice123@test.com",
                "password":"MySecurePassword123!"
            }
        )
    assert signup_response.status_code == 201

    reset_response = client.post(
            "/auth/forgot-password",
            json={
                "email":"alice123@test.com"
            }
    )

    assert reset_response.status_code == 200
    assert reset_response.json() == { "message" : (
        "If an account exists for this email, "
        "password reset instructions will be sent."
    )
}
        


