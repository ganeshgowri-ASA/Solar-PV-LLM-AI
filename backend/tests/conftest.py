"""
Pytest configuration and fixtures for testing
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.database.connection import Base, get_db
from backend.app import app


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_query_data():
    """Sample query data for testing"""
    return {
        "query_text": "What is the average efficiency of solar panels?",
        "session_id": "test-session-123"
    }


@pytest.fixture
def sample_feedback_data():
    """Sample feedback data for testing"""
    return {
        "response_id": 1,
        "rating": 5,
        "is_helpful": True,
        "is_accurate": True,
        "is_complete": True
    }


@pytest.fixture
def sample_document():
    """Sample document for testing"""
    return {
        "title": "Solar Panel Efficiency",
        "content": "Modern solar panels typically have an efficiency of 15-20%. "
                   "High-end panels can reach up to 22-23% efficiency.",
        "source_url": "https://example.com/solar-efficiency",
        "source_type": "article"
    }
