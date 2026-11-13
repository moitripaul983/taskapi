# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = (
    "postgresql+psycopg://taskapi:taskapi_dev_pw@localhost:5432/taskapi_test"
)

# Safety guard: never run destructive setup against a non-test database
assert TEST_DATABASE_URL.endswith("_test"), "Refusing to run tests on a non-test DB"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    """Give every test a clean, empty schema."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def login(client):
    """Returns a function: login('a@example.com') -> auth headers for that user."""

    def _login(email="user@example.com", password="password123"):
        client.post("/auth/signup", json={"email": email, "password": password})
        resp = client.post(
            "/auth/login", data={"username": email, "password": password}
        )
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    return _login