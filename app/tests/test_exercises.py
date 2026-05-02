import pytest

def test_create_exercise(client, auth_headers):
    exercise = {
        "name": "Тестовое упражнение",
        "muscle_group": "грудь",
        "difficulty": "beginner",
        "description": "Для тестирования"
    }
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == exercise["name"]
    assert "id" in data

def test_create_exercise_duplicate(client, auth_headers):
    exercise = {
        "name": "Тестовое упражнение 2",
        "muscle_group": "спина",
        "difficulty": "intermediate",
        "description": "Дубликат"
    }
    # Первое создание
    client.post("/exercises/", json=exercise, headers=auth_headers)

    # Второе с таким же именем
    response = client.post("/exercises/", json=exercise, headers=auth_headers)
    assert response.status_code == 400
    assert "Exercise already exists" in response.text

def test_get_exercises(client, auth_headers):
    response = client.get("/exercises/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_exercises_filter_by_muscle(client, auth_headers):
    # Создаём упражнение для фильтрации
    exercise = {
        "name": "Фильтруемое упражнение",
        "muscle_group": "грудь",
        "difficulty": "beginner",
        "description": "Для фильтрации"
    }
    client.post("/exercises/", json=exercise, headers=auth_headers)

    response = client.get("/exercises/?muscle_group=грудь", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    for exercise_item in data:
        assert exercise_item["muscle_group"] == "грудь"

def test_get_exercise_by_id(client, auth_headers):
    # Сначала создаём упражнение
    exercise = {
        "name": "Уникальное упражнение",
        "muscle_group": "ноги",
        "difficulty": "advanced",
        "description": "По ID"
    }
    create_response = client.post("/exercises/", json=exercise, headers=auth_headers)
    assert create_response.status_code == 200
    exercise_id = create_response.json()["id"]

    # Получаем по ID
    response = client.get(f"/exercises/{exercise_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == exercise["name"]

def test_get_exercise_not_found(client, auth_headers):
    response = client.get("/exercises/99999", headers=auth_headers)
    assert response.status_code == 404

def test_delete_exercise(client, auth_headers):
    # Создаём упражнение
    exercise = {
        "name": "Удаляемое упражнение",
        "muscle_group": "руки",
        "difficulty": "beginner",
        "description": "Будет удалено"
    }
    create_response = client.post("/exercises/", json=exercise, headers=auth_headers)
    assert create_response.status_code == 200
    exercise_id = create_response.json()["id"]

    # Удаляем
    response = client.delete(f"/exercises/{exercise_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.text

    # Проверяем, что удалилось
    get_response = client.get(f"/exercises/{exercise_id}", headers=auth_headers)
    assert get_response.status_code == 404
