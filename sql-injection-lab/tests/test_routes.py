import pytest

def bearer(token: str):
    return {"Authorization": f"Bearer {token}"}

def test_auth_token_injection_attempt(client):
    payloads = [
        {"name": "alice' OR '1'='1", "password": "whatever"},
        {"name": "nonexist", "password": "' OR '1'='1"},
        {"name": "' OR 1=1 --", "password": "' OR 1=1 --"},
    ]

    for body in payloads:
        r = client.post("/auth/token", json=body)
        assert r.status_code == 401, f"Possible auth SQLi: payload {body} returned {r.status_code} with body: {r.text}"

def test_order_id_path_injection_and_validation(client):
    bad_ids = ["1 OR 1=1", "1; DROP TABLE orders;", "1 UNION SELECT 1"]
    headers = bearer("secrettokenAlice")

    for bid in bad_ids:
        r = client.get(f"/orders/{bid}", headers=headers)
        assert r.status_code in (422, 404), f"Unexpected status {r.status_code} for ID {bid} body: {r.text}"

def test_authorization_header_sqli_attempt(client):
    malicious_tokens = ["' OR '1'='1", "abcd' OR '1'='1", "secrettoken123' OR '1'='1"]
    for t in malicious_tokens:
        headers = bearer(t)
        r = client.get("/orders", headers=headers)
        assert r.status_code == 401, f"Auth bypass possibility with token {t}: status {r.status_code} body: {r.text}"

def test_orders_bearer_injection(client):
    headers = bearer("badTokeh' OR '1'='1")
    
    params = {"limit": 1, "offset": "0"}
    r = client.get("/orders", headers=headers, params=params)
    assert r.status_code in (401, 403), "Injection"

def test_query_params_sql_injection_with_valid_token(client):
    headers = bearer("secrettokenAlice")
    params = {"limit": "1; DROP TABLE users --", "offset": 0}
    r = client.get("/orders", headers=headers, params=params)
    assert r.status_code in (422, 200)