import pytest


def test_auth_flow(client, db_session):
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
    old_tokens = login_response.json()
    old_refresh_token = old_tokens["refresh_token"]

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token":old_refresh_token 
        }
    )

    assert refresh_response.status_code == 200

    new_tokens = refresh_response.json()

    assert old_tokens["refresh_token"] != new_tokens["refresh_token"]

    replay_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token":old_refresh_token 
        }
    )

    assert replay_response.status_code == 401

