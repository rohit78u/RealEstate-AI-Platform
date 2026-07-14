def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_and_login(client):
    register = client.post(
        "/api/auth/register",
        json={"email": "new@test.com", "password": "password1", "full_name": "New User"},
    )
    assert register.status_code == 201
    assert register.json()["role"] == "user"

    login = client.post(
        "/api/auth/login",
        data={"username": "new@test.com", "password": "password1"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_duplicate_register(client):
    payload = {"email": "dup@test.com", "password": "password1", "full_name": "Dup User"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400


def test_protected_route_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_me(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "user@test.com"
