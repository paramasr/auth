import pytest
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password



def test_signup_session(client, db_session):
    response = client.post(
        "/auth/signup",
        json={
            "email":"alice@yahoo.com",
            "password": "@stormInTeacup123"
        }
    )

    if response.status_code == 422:
        print("\nVALIDATION ERROR DETAILS:", response.json())

    assert response.status_code == 201
    data = response.json()

    assert data["email"] == "alice@yahoo.com"
    assert "id" in data
    assert "password_hash" not in data

    #verify user created

    user = db_session.scalar(select(User).where(
        User.email == "alice@yahoo.com"
        )
    )

    assert user is not None
    assert verify_password("@stormInTeacup123", user.password_hash)

def test_duplicate_email(client, db_session):
    response1 = client.post(
        "/auth/signup",
        json={
            "email":"alice@yahoo.com",
            "password": "@stormInTeacup123"
        }
    )

    assert response1.status_code == 201

    response2 = client.post(
            "/auth/signup",
            json={
                "email":"alice@yahoo.com",
                "password": "@stormInTeacup456"
            }
    )

    assert response2.status_code == 409