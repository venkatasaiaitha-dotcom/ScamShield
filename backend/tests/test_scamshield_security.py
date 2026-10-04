import os
import pytest
from starlette.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

from backend.main import app
from backend.database.connection import init_db
from backend.security.ssrf import is_safe_external_url

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    init_db()

@pytest.fixture
def client():
    return TestClient(app, base_url="http://127.0.0.1:8000")

def test_01_register_new_user(client):
    """Test 1: User Registration creates user and returns tokens"""
    import uuid
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "SecurePassword123!"
    })
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == test_email
    assert data["user"]["role"] == "USER"

def test_02_login_and_tokens(client):
    """Test 2: Login returns valid tokens and sets HttpOnly cookie"""
    resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "access_token" in resp.cookies
    assert data["user"]["email"] == "user@scamshield.local"

def test_03_invalid_login_rejected(client):
    """Test 3: Invalid credentials return 401 Unauthorized"""
    resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "WrongPassword999!"
    })
    assert resp.status_code == 401
    assert "detail" in resp.json()

def test_04_authenticated_endpoint_me(client):
    """Test 4: Authenticated user can access /api/auth/me"""
    # Login first
    login_resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    token = login_resp.json()["access_token"]
    
    # Access /api/auth/me with Bearer token
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "user@scamshield.local"

def test_05_unauthenticated_request_rejected(client):
    """Test 5: Sensitive endpoints reject unauthenticated requests with 401"""
    # Create empty client without cookies
    fresh_client = TestClient(app, base_url="http://127.0.0.1:8000")
    endpoints = [
        ("GET", "/api/history"),
        ("GET", "/api/alerts"),
        ("GET", "/api/settings"),
        ("POST", "/api/messages/incoming"),
        ("POST", "/api/analyze/message")
    ]
    for method, path in endpoints:
        if method == "GET":
            resp = fresh_client.get(path)
        else:
            resp = fresh_client.post(path, json={})
        assert resp.status_code == 401, f"Expected 401 for {method} {path}, got {resp.status_code}"

def test_06_tenant_user_isolation(client):
    """Test 6: User A cannot see or manipulate User B's history/analyses"""
    import uuid
    # Register User A
    user_a_email = f"usera_{uuid.uuid4().hex[:6]}@example.com"
    resp_a = client.post("/api/auth/register", json={"email": user_a_email, "password": "Password123!"})
    token_a = resp_a.json()["access_token"]

    # Register User B
    user_b_email = f"userb_{uuid.uuid4().hex[:6]}@example.com"
    resp_b = client.post("/api/auth/register", json={"email": user_b_email, "password": "Password123!"})
    token_b = resp_b.json()["access_token"]

    # User A submits a message
    client.post(
        "/api/messages/incoming",
        json={"source": "SMS", "sender": "+1999888777", "content": "Private confidential message for User A"},
        headers={"Authorization": f"Bearer {token_a}"}
    )

    # User B queries their history
    resp_history_b = client.get("/api/history", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_history_b.status_code == 200
    user_b_items = resp_history_b.json()
    # Confirm User B does not see User A's private message
    assert not any("User A" in item.get("content", "") for item in user_b_items)

def test_07_normal_user_cannot_access_admin_endpoints(client):
    """Test 7: Destructive operations return 403 Forbidden for normal users"""
    login_resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    token = login_resp.json()["access_token"]

    # Normal user calls /api/gmail/wipe-data
    resp_wipe = client.post("/api/gmail/wipe-data", headers={"Authorization": f"Bearer {token}"})
    assert resp_wipe.status_code == 403
    assert resp_wipe.json().get("detail") == "Administrator privileges required"

    # Normal user calls /api/history/clear
    resp_clear = client.delete("/api/history/clear", headers={"Authorization": f"Bearer {token}"})
    assert resp_clear.status_code == 403
    assert resp_clear.json().get("detail") == "Administrator privileges required"

def test_08_admin_can_access_admin_endpoints(client):
    """Test 8: Admin role can access admin endpoints"""
    admin_resp = client.post("/api/auth/login", json={
        "email": "admin@scamshield.local",
        "password": "ScamShieldAdmin2026!"
    })
    admin_token = admin_resp.json()["access_token"]

    resp = client.post("/api/gmail/wipe-data", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json().get("status") == "success"

def test_09_webhook_without_auth_rejected(client):
    """Test 9: Webhook without signature or secret returns 401"""
    resp = client.post("/api/webhook", json={
        "source": "WEBHOOK",
        "sender": "external@gateway.com",
        "content": "Test incoming webhook message"
    })
    assert resp.status_code == 401

def test_10_webhook_with_valid_auth_accepted(client):
    """Test 10: Webhook with valid signature/secret is accepted"""
    from backend.config import SCAMSHIELD_WEBHOOK_SECRET
    resp = client.post(
        "/api/webhook",
        json={
            "source": "WEBHOOK",
            "sender": "external@gateway.com",
            "content": "Urgent alert: update your bank account now http://scam-link.xyz"
        },
        headers={"X-Webhook-Token": SCAMSHIELD_WEBHOOK_SECRET}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "received"
    assert "risk_score" in data

def test_11_rate_limiter_triggers_429(client):
    """Test 11: Rapid requests trigger 429 Too Many Requests"""
    login_resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    token = login_resp.json()["access_token"]

    hit_429 = False
    for _ in range(40):
        r = client.post(
            "/api/analyze/url",
            json={"url": "https://example.com/test"},
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 429:
            hit_429 = True
            assert "Retry-After" in r.headers
            break
    assert hit_429, "Expected rate limiter to return 429 on excessive requests"

def test_12_input_validation_limits(client):
    """Test 12: Invalid or oversized inputs are rejected"""
    from backend.security.rate_limiter import limiter
    limiter.reset()

    login_resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    token = login_resp.json()["access_token"]

    # 1. Blank content
    r1 = client.post(
        "/api/analyze/message",
        json={"content": "   "},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r1.status_code in (400, 422)

    # 2. Oversized URL (>2048 chars)
    giant_url = "https://example.com/" + ("a" * 2100)
    r2 = client.post(
        "/api/analyze/url",
        json={"url": giant_url},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r2.status_code in (400, 422)

def test_13_sql_injection_resistance(client):
    """Test 13: SQL injection payloads in queries or message contents are safe"""
    login_resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    token = login_resp.json()["access_token"]

    sqli_payload = "'; DROP TABLE analyses; SELECT * FROM users WHERE '1'='1"
    # Try searching history with SQL injection string
    r = client.get(
        f"/api/history?search={sqli_payload}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200

    # Ensure analyses table is intact
    r_stats = client.get("/api/agent/stats", headers={"Authorization": f"Bearer {token}"})
    assert r_stats.status_code == 200

def test_14_logout_invalidates_refresh_token(client):
    """Test 14: Logout invalidates refresh token and clears cookie"""
    login_resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    assert "access_token" in login_resp.cookies
    
    # Call logout
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    # Attempt refresh should fail
    refresh_resp = client.post("/api/auth/refresh")
    assert refresh_resp.status_code == 401

def test_15_ssrf_protection_blocks_internal_destinations():
    """Test 15: SSRF filter blocks localhost, private IPs, and metadata endpoints"""
    unsafe_targets = [
        "http://localhost/admin",
        "http://127.0.0.1:8000/internal",
        "http://10.0.0.1/router",
        "http://192.168.1.1/config",
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "ftp://example.com/file"
    ]
    for target in unsafe_targets:
        is_safe, reason = is_safe_external_url(target)
        assert not is_safe, f"Target {target} should have been flagged as unsafe"

    safe_target = "https://www.google.com"
    is_safe, _ = is_safe_external_url(safe_target)
    assert is_safe, f"Target {safe_target} should be safe"

def test_16_websocket_unauthorized_rejected(client):
    """Test 16: WebSocket connection without auth is rejected with 1008 policy violation"""
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/ws"):
            pass
    assert excinfo.value.code == 1008
