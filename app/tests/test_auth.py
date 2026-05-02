def test_register_success(client, test_user):
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]
    assert "id" in data

def test_register_duplicate_email(client, test_user):
    # Первая регистрация
    response1 = client.post("/auth/register", json=test_user)
    assert response1.status_code == 200

    # Вторая с таким же email
    user2 = {
        "email": test_user["email"],
        "username": "anotheruser",
        "full_name": "Another",
        "password": "password123"
    }
    response2 = client.post("/auth/register", json=user2)
    assert response2.status_code == 400
    assert "Email already registered" in response2.text

def test_register_duplicate_username(client, test_user):
    # Первая регистрация
    response1 = client.post("/auth/register", json=test_user)
    assert response1.status_code == 200

    # Вторая с таким же username
    user2 = {
        "email": "another@example.com",
        "username": test_user["username"],
        "full_name": "Another",
        "password": "password123"
    }
    response2 = client.post("/auth/register", json=user2)
    assert response2.status_code == 400
    assert "Username already taken" in response2.text

def test_login_success(client, test_user):
    # Регистрируем
    client.post("/auth/register", json=test_user)

    # Логинимся
    response = client.post(
        "/auth/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    client.post("/auth/register", json=test_user)

    response = client.post(
        "/auth/login",
        data={"username": test_user["username"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.text

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401

def test_get_current_user(client, test_user):
    # Регистрируем
    client.post("/auth/register", json=test_user)

    # Логинимся
    login_response = client.post(
        "/auth/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    token = login_response.json()["access_token"]

    # Получаем текущего пользователя
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]

def test_protected_endpoint_without_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.text
