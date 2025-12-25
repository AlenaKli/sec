import hashlib
import time
import bcrypt
from validation import validate_password
from user import User, UserStorage
from config import config
from logger import auth_logger

def calculate_delay(failed_attempts: int) -> float:
    if failed_attempts <= 0:
        return 0.0
    return (config.delay_base ** failed_attempts) + config.delay_constant

def should_reset_counter(user: User) -> bool:
    if user.failed_attempts == 0:
        return False
    
    if user.last_failed_time > 0:
        time_passed = time.time() - user.last_failed_time
        return time_passed > config.reset_counter_after
    
    return False

def register_user(storage: UserStorage, username: str, email: str, password: str) -> User:
    if User.exists(storage, username):
        raise ValueError(f"Пользователь {username} уже существует")
    
    validate_password(password)
    
    bcrypt_hash = bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt(rounds=config.bcrypt_rounds)
    ).decode('utf-8')
    
    user = User(
        username=username, 
        email=email, 
        password_hash=bcrypt_hash,
        failed_attempts=0,
        last_failed_time=0.0,
        backoff_seconds=0.0
    )
    user.save(storage)
    
    auth_logger.info(f"Зарегистрирован новый пользователь: {username}")
    return user

def verify_credentials(storage: UserStorage, username: str, password: str) -> bool:
    user = User.load(storage, username)
    if user is None:
        auth_logger.warning(f"Попытка входа несуществующего пользователя: {username}")
        return False
    
    current_time = time.time()
    
    if should_reset_counter(user):
        user.failed_attempts = 0
        user.backoff_seconds = 0.0
        user.last_failed_time = 0.0
        user.save(storage)
        auth_logger.info(f"Сброшен счетчик неудачных попыток для пользователя: {username}")
    
    if user.failed_attempts > 0 and user.last_failed_time > 0:
        expected_delay = calculate_delay(user.failed_attempts)
        time_since_last_failure = current_time - user.last_failed_time
        
        if time_since_last_failure < expected_delay:
            sleep_time = expected_delay - time_since_last_failure
            if sleep_time > 0:
                auth_logger.info(
                    f"Применена задержка {sleep_time:.2f}с для {username} "
                    f"(попытка {user.failed_attempts})"
                )
                time.sleep(sleep_time)
    
    is_valid = False
    
    if user.password_hash.startswith("$2"):
        is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
    else:
        md5_hex = hashlib.md5(password.encode("utf-8")).hexdigest()
        if user.password_hash == md5_hex:
            is_valid = True
            user.password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt(rounds=config.bcrypt_rounds)
            ).decode('utf-8')
            auth_logger.info(f"Мигрирован пользователь {username} с MD5 на bcrypt")
    
    if is_valid:
        old_attempts = user.failed_attempts
        user.failed_attempts = 0
        user.backoff_seconds = 0.0
        user.last_failed_time = 0.0
        user.save(storage)
        
        if config.log_successful_logins:
            auth_logger.info(f"Успешный вход: {username}")
        
        if old_attempts > 0:
            auth_logger.info(f"Сброшен счетчик неудач для {username} (было: {old_attempts})")
        
        return True
    else:
        user.failed_attempts += 1
        user.backoff_seconds = calculate_delay(user.failed_attempts)
        user.last_failed_time = time.time()
        user.save(storage)
        
        if config.log_failed_attempts:
            auth_logger.warning(
                f"Неудачная попытка входа: {username} "
                f"(попытка {user.failed_attempts}, задержка: {user.backoff_seconds:.2f}с)"
            )
        
        time.sleep(user.backoff_seconds)
        
        return False

def is_account_locked(storage: UserStorage, username: str) -> bool:
    user = User.load(storage, username)
    if user is None:
        return False
    return False

def reset_failed_attempts(storage: UserStorage, username: str, admin: str = "system") -> bool:
    user = User.load(storage, username)
    if user is None:
        return False
    
    old_attempts = user.failed_attempts
    user.failed_attempts = 0
    user.backoff_seconds = 0.0
    user.last_failed_time = 0.0
    user.save(storage)
    
    auth_logger.info(
        f"Администратор {admin} сбросил счетчик неудачных попыток "
        f"для пользователя {username} (было: {old_attempts})"
    )
    return True