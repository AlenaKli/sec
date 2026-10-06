from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.database import users_db
from src.schemas import UserCreate
from src.security import pwd_context, create_access_token
from src.logger_config import logger

router = APIRouter()


@router.post("/registration")
def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already taken")
    users_db[user.username] = {
        "username": user.username,
        "role": "user",
        "hashed_password": pwd_context.hash(user.password),
    }
    logger.info("New user registered: %s", user.username)
    return {"msg": "User created", "user": user.username}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        logger.warning("Failed login attempt for username: %s", form_data.username)
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    logger.info("User logged in: %s", form_data.username)
    return {"access_token": token, "token_type": "bearer"}
