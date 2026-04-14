import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# ==============================================================================
# 1. Setup In-Memory Database for Testing
# ==============================================================================
# SQLite runs entirely in RAM, making it incredibly fast and completely isolated.
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Keeps the connection alive for the duration of the test
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ==============================================================================
# 2. Dependency Injection Override
# ==============================================================================
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Force FastAPI to use our SQLite db instead of the real PostgreSQL db
app.dependency_overrides[get_db] = override_get_db

# Create the client that will make "HTTP" requests to our app
client = TestClient(app)


# ==============================================================================
# 3. Test Fixtures
# ==============================================================================
@pytest.fixture(autouse=True)
def setup_and_teardown_database():
    """This runs automatically before and after EVERY single test.
    It creates the tables, runs the test, and then drops the tables.
    This guarantees every test starts with a 100% clean slate.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ==============================================================================
# 4. The Actual Tests
# ==============================================================================


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "shadowtag_v4-fastapi-services"}


def test_create_user():
    response = client.post(
        "/users", json={"email": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "redacted@shadowtag-v4.local"
    assert "id" in data
    assert data["is_active"] is True
    # Ensure the password is NOT returned in the response!
    assert "password" not in data
    assert "hashed_password" not in data


def test_create_existing_user():
    # 1. Create the first user
    client.post(
        "/users", json={"email": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )

    # 2. Try to create the exact same user again
    response = client.post(
        "/users", json={"email": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )

    # 3. Verify the API successfully rejected it
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
