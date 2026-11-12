import pytest
from sqlalchemy import select
from app.models.user import User
from app.core.security import verify_password
from app.core.jwt import (
    create_access_token,
    decode_access_token
)

token = create_access_token("test-user-id")

print(decode_access_token(token))

def test_login_flow(client, db_session):
    signup_response = client.post(
        "/auth/signup",
        json={
            "email":"alice123@test.com",
            "password":"MySecurePassword123!"
        }
    )

    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email":"alice123@test.com",
            "password":"MySecurePassword123!"
        }
    )

    assert login_response.status_code == 200
    token_data = login_response.json()
    

    assert token_data["token_type"] == "Bearer"
    token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    print("Decoded JWT:", decode_access_token(token))

    #access restricted api

    user_response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    

    assert user_response.status_code == 200
    user = user_response.json()
    assert user["email"] == "alice123@test.com"

    #access without token
    no_token_response = client.get(
        "/users/me"
    )

    assert no_token_response.status_code == 401

    #access with invalid token
    user_response = client.get(
            "/users/me",
            headers={
                "Authorization": "Bearer invalid_token"
            }
        )
        
    
    assert user_response.status_code == 401
    