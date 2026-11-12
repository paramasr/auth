import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.session import Base, get_db
from app.main import app
from alembic import command
from alembic.config import Config

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://authuser:local_dev_password@localhost:5432/authdb_test"
)

test_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    test_database_url = DATABASE_URL

    assert test_database_url.endswith("/authdb_test"), (
        "Migrations must only run against authdb_test"
    )

    previous_url = os.environ.get("DATABASE_URL")

    os.environ["DATABASE_URL"] = test_database_url

    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        yield
    finally:
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url



@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    #allows test to commit without committing the outer trx
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db]=override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


