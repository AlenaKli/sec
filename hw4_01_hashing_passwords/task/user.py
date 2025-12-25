# user.py
from dataclasses import dataclass, field
from typing import Protocol, Optional, Dict
import time


class UserStorage(Protocol):
    def get_user(self, username: str) -> Optional[Dict]: ...
    def save_user(self, record: Dict) -> None: ...
    def exists(self, username: str) -> bool: ...


@dataclass
class User:
    username: str
    email: str
    password_hash: str
    failed_attempts: int = field(default=0)  
    last_failed_time: float = field(default=0.0)  
    backoff_seconds: float = field(default=0.0)  
    
    def save(self, storage: UserStorage) -> None:
        storage.save_user({
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "failed_attempts": self.failed_attempts,
            "last_failed_time": self.last_failed_time,
            "backoff_seconds": self.backoff_seconds,
        })
    
    @classmethod
    def load(cls, storage: UserStorage, username: str) -> Optional["User"]:
        rec = storage.get_user(username)
        if rec is None:
            return None
        
        failed_attempts = rec.get("failed_attempts", 0)
        last_failed_time = rec.get("last_failed_time", 0.0)
        backoff_seconds = rec.get("backoff_seconds", 0.0)
        
        return cls(
            username=rec["username"],
            email=rec["email"],
            password_hash=rec["password_hash"],
            failed_attempts=failed_attempts,
            last_failed_time=last_failed_time,
            backoff_seconds=backoff_seconds
        )
    
    @classmethod
    def exists(cls, storage: UserStorage, username: str) -> bool:
        return storage.exists(username)


class InMemoryUserStorage:
    """Учебное хранилище на словаре."""
    def __init__(self) -> None:
        self._db: Dict[str, Dict] = {}
    
    def get_user(self, username: str) -> Optional[Dict]:
        return self._db.get(username)
    
    def save_user(self, record: Dict) -> None:
        self._db[record["username"]] = dict(record)
    
    def exists(self, username: str) -> bool:
        return username in self._db