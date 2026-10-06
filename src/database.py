from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_db: dict = {
    "alice": {
        "username": "alice",
        "role": "user",
        "hashed_password": _pwd.hash("Alice123!"),
    },
    "bob": {
        "username": "bob",
        "role": "user",
        "hashed_password": _pwd.hash("Bob12345!"),
    },
    "admin": {
        "username": "admin",
        "role": "admin",
        "hashed_password": _pwd.hash("Admin123!"),
    },
}

files_db: list = [
    {"id": 1, "filename": "report_alice.pdf", "owner": "alice", "size": 1024, "path": "", "is_encrypted": False},
    {"id": 2, "filename": "photo_bob.jpg", "owner": "bob", "size": 2048, "path": "", "is_encrypted": False},
    {"id": 3, "filename": "admin_keys.txt", "owner": "admin", "size": 12, "path": "", "is_encrypted": False},
]

comments: list = []
file_id_counter: list = [3]
