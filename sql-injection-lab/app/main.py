from fastapi import FastAPI, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, Any
from .database import get_db
from .auth import get_user_by_token
from .models import User, Token, Order, Good
from pydantic import BaseModel
import bcrypt
import secrets

app = FastAPI(
    title="SQL Injection Lab - ORM Edition",
    description="Защищенное API с использованием SQLAlchemy ORM",
    version="2.0.0"
)

class AuthRequest(BaseModel):
    name: str
    password: str

@app.post("/auth/token")
async def auth_token(
    body: AuthRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.name == body.name)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(body.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    result = await db.execute(
        select(Token).where(
            Token.user_id == user.id,
            Token.is_valid == True
        ).limit(1)
    )
    existing_token = result.scalar_one_or_none()
    
    if existing_token:
        token = existing_token.value
    else:
        token = secrets.token_urlsafe(64)
        new_token = Token(value=token, user_id=user.id)
        db.add(new_token)
        await db.commit()
    
    return {"token": token}

@app.get("/orders")
async def list_orders(
    user: Annotated[dict[str, Any], Depends(get_user_by_token)],
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user["id"])
        .order_by(Order.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    orders = result.scalars().all()
    
    return [{
        "id": order.id,
        "user_id": order.user_id,
        "created_at": order.created_at.isoformat()
    } for order in orders]

@app.get("/orders/{order_id}")
async def order_details(
    user: Annotated[dict[str, Any], Depends(get_user_by_token)],
    order_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user["id"]
        )
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    result = await db.execute(
        select(Good).where(Good.order_id == order_id)
    )
    goods = result.scalars().all()
    
    return {
        "order": {
            "id": order.id,
            "user_id": order.user_id,
            "created_at": order.created_at.isoformat()
        },
        "goods": [{
            "id": g.id,
            "name": g.name,
            "count": g.count,
            "price": float(g.price)
        } for g in goods]
    }

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        return {"status": "healthy", "orm": "sqlalchemy"}
    except Exception:
        return {"status": "unhealthy", "orm": "sqlalchemy"}