from fastapi import HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import Token, User

async def get_user_by_token(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    
    token_value = authorization[7:].strip()
    
    if not token_value:
        raise HTTPException(status_code=401, detail="Empty token")
    
    result = await db.execute(
        select(User)
        .join(Token, Token.user_id == User.id)
        .where(Token.value == token_value)
        .where(Token.is_valid == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"id": user.id, "name": user.name}