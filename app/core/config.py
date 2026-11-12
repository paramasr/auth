import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY must be configured "
        "with at least 32 characters"
    )

JWT_ALGORITHM = "HS256"

JWT_ISSUER = "auth-service"

JWT_AUDIENCE = "auth-api"

ACCESS_TOKEN_EXPIRE_MINUTES = 15

REFRESH_TOKEN_EXPIRE_DAYS = 7

PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 30