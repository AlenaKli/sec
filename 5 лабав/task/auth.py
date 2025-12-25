import hashlib
import time
from passlib.context import CryptContext
from validation import validate_password
from user import User, UserStorage

pwd_context = CryptContext(schemes=["argon2"])

def register_user(storage: UserStorage, username: str, email: str, password: str) -> User:
    """
    Создает пользователя и сохраняет хэш пароля в виде md5.
    ВАЖНО: md5 используется ИСКЛЮЧИТЕЛЬНО как учебный старт.
    Далее это будет мигрировано на Argon2/bcrypt.
    """
    if User.exists(storage, username):
        raise ValueError("Пользователь с таким username уже существует")

    validate_password(password)

    password_hash = pwd_context.hash(password)
    user = User(username=username, email=email, password_hash=password_hash)
    user.save(storage)
    return user

def is_account_locked(storage: UserStorage, username: str) -> bool:
    user = User.load(storage, username)
    if user is None:
        return False
    return user.is_locked


def verify_credentials(storage: UserStorage, username: str, password: str) -> bool:
    """
    Возвращает True, если пользователь существует и md5(password) совпадает с сохраненным.
    """
    user = User.load(storage, username)
    if user is None:
        return False
    
    if user.is_locked:
        return False
    
    password_correct = False
    migration_needed = False

    if user.password_hash.startswith("$argon2"):
        password_correct = pwd_context.verify(password, user.password_hash)
    else:
        md5_hex = hashlib.md5(password.encode("utf-8")).hexdigest()
        password_correct = (user.password_hash == md5_hex)
        migration_needed = password_correct

    if password_correct:
        user.failed_login_attempts = 0
        user.is_locked = False
        
        if migration_needed:
            user.password_hash = pwd_context.hash(password)
        
        user.save(storage)
        return True
    else:
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= 5:
            user.is_locked = True
        
        user.save(storage)
        return False