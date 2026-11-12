from fastapi import FastAPI
from sqlalchemy import text
from app.api.auth import router as auth_router
from app.api.users import router as users_router

from app.db.session import engine

app = FastAPI(title="Authentication Service")
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/db")
def database_health():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "connected"}
