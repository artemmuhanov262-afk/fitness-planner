def test_create_workout(client, auth_headers):
    workout = {
        "title": "Тестовая тренировка",
        "description": "Тестовая тренировка для проверки",
        "duration_minutes": 45
    }
    response = client.post("/workouts/", json=workout, headers=auth_headers)
    # FastAPI возвращает 201 Created для POST запросов
    assert response.status_code == 201  # или 200, но 201 правильнее
    data = response.json()
    assert data["title"] == workout["title"]
    assert data["user_id"] is not None
    assert "id" in data

def test_delete_workout(client, auth_headers):
    # Создаём тренировку
    workout = {
        "title": "Удаляемая тренировка",
        "description": "Будет удалена",
        "duration_minutes": 20
    }
    create_response = client.post("/workouts/", json=workout, headers=auth_headers)
    workout_id = create_response.json()["id"]

    # Удаляем (FastAPI DELETE возвращает 204 No Content)
    response = client.delete(f"/workouts/{workout_id}", headers=auth_headers)
    assert response.status_code == 204  # Изменил 200 на 204

    # Проверяем, что удалилось
    get_response = client.get(f"/workouts/{workout_id}", headers=auth_headers)
    assert get_response.status_code == 404
