import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

async def seed_database():
    url = os.getenv('DATABASE_URL').replace('postgresql://', 'postgresql+asyncpg://')
    engine = create_async_engine(url, echo=True)
    
    async with engine.connect() as conn:
        await conn.execute(text("DELETE FROM goods"))
        await conn.execute(text("DELETE FROM orders"))
        await conn.execute(text("DELETE FROM tokens"))
        await conn.execute(text("DELETE FROM users"))
        await conn.commit()
        
        users = [
            {"name": "alice", "password_hash": bcrypt.hashpw(b"password1", bcrypt.gensalt()).decode()},
            {"name": "bob", "password_hash": bcrypt.hashpw(b"password2", bcrypt.gensalt()).decode()},
            {"name": "eva", "password_hash": bcrypt.hashpw(b"password3", bcrypt.gensalt()).decode()},
        ]
        
        user_ids = {}
        for user in users:
            result = await conn.execute(
                text("INSERT INTO users (name, password_hash) VALUES (:name, :password_hash) RETURNING id"),
                user
            )
            user_id = result.scalar()
            user_ids[user["name"]] = user_id
            await conn.commit()
        
        tokens = [
            {"value": "secrettokenAlice", "user_id": user_ids["alice"], "is_valid": True},
            {"value": "secrettokenBob", "user_id": user_ids["bob"], "is_valid": True},
            {"value": "secrettokenEva", "user_id": user_ids["eva"], "is_valid": True},
        ]
        
        for token in tokens:
            await conn.execute(
                text("INSERT INTO tokens (value, user_id, is_valid) VALUES (:value, :user_id, :is_valid)"),
                token
            )
            await conn.commit()
        
        orders = [
            {"user_id": user_ids["alice"]},
            {"user_id": user_ids["bob"]},
            {"user_id": user_ids["eva"]},
            {"user_id": user_ids["alice"]},
        ]
        
        order_ids = []
        for order in orders:
            result = await conn.execute(
                text("INSERT INTO orders (user_id) VALUES (:user_id) RETURNING id"),
                order
            )
            order_id = result.scalar()
            order_ids.append(order_id)
            await conn.commit()
        
        goods = [
            {"name": "widget", "order_id": order_ids[0], "count": 3, "price": 9.99},
            {"name": "widget", "order_id": order_ids[0], "count": 4, "price": 10.99},
            {"name": "widget", "order_id": order_ids[1], "count": 5, "price": 1.99},
            {"name": "widget", "order_id": order_ids[1], "count": 6, "price": 2.99},
            {"name": "widget", "order_id": order_ids[2], "count": 1, "price": 3.99},
            {"name": "widget", "order_id": order_ids[2], "count": 2, "price": 4.99},
            {"name": "widget", "order_id": order_ids[3], "count": 3, "price": 5.99},
            {"name": "widget", "order_id": order_ids[3], "count": 4, "price": 6.99},
        ]
        
        for good in goods:
            await conn.execute(
                text("INSERT INTO goods (name, order_id, count, price) VALUES (:name, :order_id, :count, :price)"),
                good
            )
            await conn.commit()
        
        print('Тестовые данные успешно добавлены!')
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_database())