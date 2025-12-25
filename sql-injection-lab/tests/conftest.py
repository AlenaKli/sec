import pytest
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.database import get_db
from app.models import Base
from app.main import app
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv("DATABASE_URL").replace(
    "postgresql://", "postgresql+asyncpg://"
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = async_sessionmaker(
        engine, 
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    yield TestingSessionLocal

@pytest.fixture(scope="function")
async def client(test_db):
    async def override_get_db():
        async with test_db() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with test_db() as session:
        from app.models import User, Token, Order, Good
        import hashlib
        
        users = []
        user_data = [
            ("alice", hashlib.md5(b"password1").hexdigest()),
            ("bob", hashlib.md5(b"password2").hexdigest()),
            ("eva", hashlib.md5(b"password3").hexdigest()),
        ]
        
        for name, password_hash in user_data:
            user = User(name=name, password_hash=password_hash)
            session.add(user)
            users.append(user)
        
        await session.flush()
        
        tokens_data = [
            ("secrettokenAlice", users[0].id),
            ("secrettokenBob", users[1].id),
            ("secrettokenEva", users[2].id),
        ]
        
        for value, user_id in tokens_data:
            token = Token(value=value, user_id=user_id)
            session.add(token)
        
        await session.flush()
        
        orders = []
        for user in users:
            order = Order(user_id=user.id)
            session.add(order)
            orders.append(order)
        
        await session.flush()
        
        goods_data = [
            ("widget", orders[0].id, 3, 9.99),
            ("widget", orders[0].id, 4, 10.99),
            ("widget", orders[1].id, 5, 1.99),
        ]
        
        for name, order_id, count, price in goods_data:
            good = Good(name=name, order_id=order_id, count=count, price=price)
            session.add(good)
        
        await session.commit()
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()