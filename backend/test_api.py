from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_features_requires_authentication():
    response = client.get("/api/features")

    assert response.status_code == 401


def test_login():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testbeneficiary",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Login successful"
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_wrong_password():
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testbeneficiary",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


def test_protected_profile_without_token():
    response = client.get(
        "/api/profiles/1"
    )

    assert response.status_code == 401


def test_protected_profile_with_token():
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "testbeneficiary",
            "password": "Test@12345",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/profiles/1",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200
    assert "profile" in response.json()