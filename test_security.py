from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def get_token(username: str, password: str) -> str:
    r = client.post("/login", data={"username": username, "password": password})
    assert r.status_code == 200, f"Login failed for {username}: {r.text}"
    return r.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_idor_blocked():
    token = get_token("alice", "Alice123!")
    r = client.get("/files/2", headers=auth(token))
    assert r.status_code == 404, f"IDOR: alice accessed bob's file, got {r.status_code}"
    print("PASS test_idor_blocked")


def test_own_file_accessible():
    token = get_token("alice", "Alice123!")
    r = client.get("/files/1", headers=auth(token))
    assert r.status_code == 200, f"Alice cannot access her own file: {r.status_code}"
    print("PASS test_own_file_accessible")


def test_admin_can_delete_any_file():
    token = get_token("admin", "Admin123!")
    r = client.delete("/files/2", headers=auth(token))
    assert r.status_code == 200, f"Admin delete failed: {r.status_code}"
    print("PASS test_admin_can_delete_any_file")


if __name__ == "__main__":
    test_idor_blocked()
    test_own_file_accessible()
    test_admin_can_delete_any_file()
    print("\nAll tests passed.")
