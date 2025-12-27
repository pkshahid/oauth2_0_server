import pytest
from fastapi.testclient import TestClient
from ..app.main import app
from ..app.db.session import SessionLocal

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()