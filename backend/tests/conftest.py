"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.config import get_settings
from app.models import (
    Hotel,
    Staff,
    Conversation,
    Message,
    Ticket,
    RoutingRule,
)


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/inconnect_test"


# Test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"server_settings": {"timezone": "UTC"}},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
async def setup_database():
    """Setup test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


    await test_engine.dispose()


@pytest.fixture
async def db_session(setup_database: AsyncGenerator) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session"""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator:
    """Create test client with database override"""
    from fastapi.testclient import TestClient
    from app.main import app

    from app.core.database import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sync_db():
    """Create synchronous test database session"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    sync_engine = create_engine(
        "postgresql://postgres:postgres@localhost:5432/inconnect_test",
        poolclass=StaticPool,
    )

    Base.metadata.create_all(sync_engine)

    TestingSessionLocal = sessionmaker(bind=sync_engine)

    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(sync_engine)
    sync_engine.dispose()


# Test data fixtures
@pytest.fixture
def test_hotel() -> dict:
    """Test hotel data"""
    return {
        "id": "test-hotel-001",
        "name": "测试度假村",
        "code": "TEST001",
        "address": "测试地址123号",
        "phone": "400-123-4567",
        "is_active": True,
    }


@pytest.fixture
def test_staff(test_hotel: dict) -> dict:
    """Test staff data"""
    return {
        "id": "test-staff-001",
        "hotel_id": test_hotel["id"],
        "name": "张三",
        "wechat_userid": "zhangsan_wx",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "role": "staff",
        "department": "客房部",
        "status": "active",
        "is_available": True,
    }


@pytest.fixture
def test_conversation(test_hotel: dict) -> dict:
    """Test conversation data"""
    return {
        "id": "test-conv-001",
        "hotel_id": test_hotel["id"],
        "guest_id": "guest_wx_001",
        "guest_name": "李四",
        "guest_phone": "13900139000",
        "status": "active",
    }


@pytest.fixture
def test_ticket(test_hotel: dict, test_conversation: dict, test_staff: dict) -> dict:
    """Test ticket data"""
    return {
        "id": "test-ticket-001",
        "hotel_id": test_hotel["id"],
        "conversation_id": test_conversation["id"],
        "assigned_to": test_staff["id"],
        "title": "房间空调故障",
        "description": "302房间空调不制冷",
        "category": "maintenance",
        "priority": "P2",
        "status": "pending",
    }
