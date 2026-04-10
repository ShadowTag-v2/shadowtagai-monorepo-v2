"""
Unit tests for Support Builder feature.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import Base, get_db
from src.main import app

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_support_builder.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
async def setup_database():
    """Setup test database before each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_faq(setup_database):
    """Test creating a new FAQ."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/support-builder/faqs",
            json={
                "question": "How do I reset my password?",
                "answer": "Click on 'Forgot Password' and follow the instructions.",
                "category": "Account",
                "tags": ["password", "account", "security"],
                "priority": 5,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["question"] == "How do I reset my password?"
        assert data["category"] == "Account"
        assert "id" in data


@pytest.mark.asyncio
async def test_get_faqs(setup_database):
    """Test getting list of FAQs."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create some FAQs first
        await client.post(
            "/api/support-builder/faqs",
            json={
                "question": "Test question 1?",
                "answer": "Test answer 1",
                "category": "General",
            },
        )
        await client.post(
            "/api/support-builder/faqs",
            json={
                "question": "Test question 2?",
                "answer": "Test answer 2",
                "category": "General",
            },
        )

        # Get FAQs
        response = await client.get("/api/support-builder/faqs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2


@pytest.mark.asyncio
async def test_search_faqs(setup_database):
    """Test searching FAQs."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a FAQ
        await client.post(
            "/api/support-builder/faqs",
            json={
                "question": "How do I enable two-factor authentication?",
                "answer": "Go to Settings > Security > Enable 2FA",
                "category": "Security",
            },
        )

        # Search for it
        response = await client.post(
            "/api/support-builder/faqs/search",
            json={"query": "two-factor", "limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "two-factor" in data[0]["question"].lower()


@pytest.mark.asyncio
async def test_create_help_article(setup_database):
    """Test creating a help article."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/support-builder/articles",
            json={
                "title": "Getting Started Guide",
                "slug": "getting-started-guide",
                "content": "This is a comprehensive guide to getting started...",
                "excerpt": "Learn the basics",
                "category": "Guides",
                "tags": ["beginner", "tutorial"],
                "author": "Support Team",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Getting Started Guide"
        assert data["slug"] == "getting-started-guide"


@pytest.mark.asyncio
async def test_create_widget_config(setup_database):
    """Test creating a chat widget configuration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/support-builder/widget-configs",
            json={
                "name": "Default Support Chat",
                "description": "Main customer support chat widget",
                "primary_color": "#007bff",
                "position": "bottom-right",
                "greeting_message": "Hi! How can we help you today?",
                "ai_system_prompt": "You are a helpful customer support assistant.",
                "ai_model": "claude-3-sonnet-20240229",
                "temperature": 0.7,
                "max_tokens": 1024,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Default Support Chat"
        assert data["primary_color"] == "#007bff"


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/support-builder/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "features" in data
        assert "Chat widgets" in data["features"]
