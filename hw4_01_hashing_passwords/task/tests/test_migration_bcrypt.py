import hashlib
import bcrypt
import auth
from user import InMemoryUserStorage, User

def test_md5_user_is_migrated_to_bcrypt_on_successful_login():
    store = InMemoryUserStorage()
    username = "bob"
    raw = "S3curePass!"
    md5_hex = hashlib.md5(raw.encode()).hexdigest()
    User(username=username, email="bob@example.com", password_hash=md5_hex).save(store)
    
    assert auth.verify_credentials(store, username, raw) is True
    migrated = User.load(store, username)
    assert migrated is not None
    assert bcrypt.checkpw(raw.encode('utf-8'), migrated.password_hash.encode('utf-8'))

def test_register_stores_bcrypt_hash():
    store = InMemoryUserStorage()
    _ = auth.register_user(store, "bob", "bob@example.com", "S3curePass!")
    saved = User.load(store, "bob")
    assert saved is not None
    assert bcrypt.checkpw("S3curePass!".encode('utf-8'), saved.password_hash.encode('utf-8'))