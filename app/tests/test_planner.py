import pytest

def test_generate_plan_success(client, auth_headers):
    # Сначала добавим несколько упражнений в БД
    exercises = [
        {"name": "Тест жим", "muscle_group": "грудь", "difficulty": "intermediate", "description": "Тест"},
        {"name": "Тест присед", "muscle_group": "ноги", "difficulty": "intermediate", "description": "Тест"},
        {"name": "Тест тяга", "muscle_group": "спина", "difficulty": "intermediate", "description": "Тест"},
    ]

    for ex in exercises:
        client.post("/exercises/", json=ex, headers=auth_headers)

    # Генерируем план
    plan_request = {
        "goal": "balance",
        "days_per_week": 4,
        "level": "intermediate"
    }
    response = client.post("/plan/generate", json=plan_request, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["goal"] == "balance"
    assert data["level"] == "intermediate"
    assert data["days_per_week"] == 4
    assert "weekly_plan" in data
    assert len(data["weekly_plan"]) == 4
    assert "recommendations" in data

def test_generate_plan_invalid_goal(client, auth_headers):
    plan_request = {
        "goal": "invalid_goal",
        "days_per_week": 4,
        "level": "intermediate"
    }
    response = client.post("/plan/generate", json=plan_request, headers=auth_headers)
    assert response.status_code == 400
    assert "Goal must be" in response.text

def test_generate_plan_invalid_days(client, auth_headers):
    plan_request = {
        "goal": "balance",
        "days_per_week": 10,
        "level": "intermediate"
    }
    response = client.post("/plan/generate", json=plan_request, headers=auth_headers)
    assert response.status_code == 400
    assert "Days per week must be between 1 and 7" in response.text

def test_generate_plan_invalid_level(client, auth_headers):
    plan_request = {
        "goal": "balance",
        "days_per_week": 4,
        "level": "expert"
    }
    response = client.post("/plan/generate", json=plan_request, headers=auth_headers)
    assert response.status_code == 400
    assert "Level must be one of" in response.text

def test_generate_plan_strength_goal(client, auth_headers):
    plan_request = {
        "goal": "strength",
        "days_per_week": 3,
        "level": "beginner"
    }
    response = client.post("/plan/generate", json=plan_request, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Для strength цели должно быть меньше повторений
    for day in data["weekly_plan"]:
        for exercise in day["exercises"]:
            assert exercise["reps"] <= 10

def test_generate_plan_endurance_goal(client, auth_headers):
    plan_request = {
        "goal": "endurance",
        "days_per_week": 5,
        "level": "intermediate"
    }
    response = client.post("/plan/generate", json=plan_request, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    for day in data["weekly_plan"]:
        for exercise in day["exercises"]:
            assert exercise["reps"] >= 10

def test_generate_plan_without_auth(client):
    plan_request = {
        "goal": "balance",
        "days_per_week": 4,
        "level": "intermediate"
    }
    response = client.post("/plan/generate", json=plan_request)
    assert response.status_code == 401

