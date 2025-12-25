from typing import Any, Tuple
import time
import crypto
import user as user_module
import storage

def record_token(payload: dict[str, Any]) -> None:
    """Сохраняет токен в базу для отслеживания отзывов"""
    db = storage.load_tokens()
    db["tokens"].append({
        "jti": payload["jti"],
        "sub": payload["sub"],
        "typ": payload["typ"],
        "exp": payload["exp"],
        "revoked": False,
    })
    storage.save_tokens(db)

def revoke_by_jti(jti: str) -> None:
    """Отзывает токен по его jti"""
    db = storage.load_tokens()
    for token in db["tokens"]:
        if token["jti"] == jti:
            token["revoked"] = True
    storage.save_tokens(db)

def is_revoked(jti: str) -> bool:
    """Проверяет, отозван ли токен"""
    db = storage.load_tokens()
    for token in db["tokens"]:
        if token["jti"] == jti:
            return token.get("revoked", False)
    return False

def is_expired(exp: int) -> bool:
    """Проверяет, истек ли срок действия токена"""
    return int(time.time()) >= exp

def login(username: str, password: str) -> Tuple[str, str]:
    """Аутентификация пользователя и выдача пары токенов"""
    u = user_module.get_user(username)
    if u is None:
        raise ValueError("user not found")
    
    if not user_module.verify_password(u, password):
        raise ValueError("invalid password")
    
    # Генерируем access и refresh токены
    access_token, access_payload = crypto.issue_access(username)
    refresh_token, refresh_payload = crypto.issue_refresh(username)
    
    # Сохраняем токены в базу
    record_token(access_payload)
    record_token(refresh_payload)
    
    return access_token, refresh_token

def verify_access(access: str) -> dict[str, Any]:
    """Проверяет access токен и возвращает payload"""
    try:
        payload = crypto.decode(access)
    except Exception as e:
        if "expired" in str(e).lower():
            raise ValueError("token expired")
        raise ValueError("invalid token signature")
    
    # Проверка типа токена
    if payload.get("typ") != "access":
        raise ValueError("wrong token type")
    
    # Проверка отзыва
    if is_revoked(payload["jti"]):
        raise ValueError("token revoked")
    
    # Проверка истечения срока
    if is_expired(payload["exp"]):
        raise ValueError("token expired")
    
    return payload

def refresh_pair(refresh_token: str) -> Tuple[str, str]:
    """Ротация токенов: выдает новую пару, старый refresh отзывается"""
    try:
        payload = crypto.decode(refresh_token)
    except Exception:
        raise ValueError("invalid refresh token")
    
    # Проверка типа токена
    if payload.get("typ") != "refresh":
        raise ValueError("wrong token type - expected refresh")
    
    # Проверка отзыва
    if is_revoked(payload["jti"]):
        raise ValueError("refresh token revoked")
    
    # Проверка истечения срока
    if is_expired(payload["exp"]):
        raise ValueError("refresh token expired")
    
    # Отзываем старый refresh токен
    revoke_by_jti(payload["jti"])
    
    # Генерируем новую пару
    username = payload["sub"]
    new_access, access_payload = crypto.issue_access(username)
    new_refresh, refresh_payload = crypto.issue_refresh(username)
    
    # Сохраняем новые токены
    record_token(access_payload)
    record_token(refresh_payload)
    
    return new_access, new_refresh

def revoke(token: str) -> None:
    """Отзыв токена (access или refresh)"""
    try:
        payload = crypto.decode(token)
        revoke_by_jti(payload["jti"])
    except Exception:
        raise ValueError("invalid token")

def introspect(token: str) -> dict[str, Any]:
    """Интроспекция токена: проверка активности и возврат metadata"""
    try:
        payload = crypto.decode(token)
        active = (not is_revoked(payload["jti"])) and (not is_expired(payload["exp"]))
        return {
            "active": active,
            "sub": payload.get("sub"),
            "typ": payload.get("typ"),
            "exp": payload.get("exp"),
            "jti": payload.get("jti"),
        }
    except Exception:
        return {"active": False, "error": "invalid_token"}