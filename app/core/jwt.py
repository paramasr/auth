from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ISSUER,
    JWT_AUDIENCE,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": str(uuid4())
    }

    token = jwt.encode(payload, JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token, 
        JWT_SECRET_KEY, 
        algorithms=[JWT_ALGORITHM],
        audience=JWT_AUDIENCE,        
        issuer=JWT_ISSUER,
        options={
            "require" : [
                "sub",
                "iss",
                "aud",
                "iat",
                "exp",
                "jti"
            ]
        })
