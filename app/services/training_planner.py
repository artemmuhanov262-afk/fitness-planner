from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Exercise
import random

class TrainingPlanner:
    """Генератор плана тренировок с жёстким соблюдением фокуса дня"""

    def __init__(self, db: Session):
        self.db = db

    def generate_plan(self, goal: str, days_per_week: int, level: str) -> Dict[str, Any]:
        """Генерация плана с точным соблюдением групп мышц для каждого дня"""

        all_exercises = self.db.query(Exercise).all()

        if not all_exercises:
            return self._get_fallback_plan(goal, level, days_per_week)

        # Группируем по группам мышц (нормализуем названия)
        exercises_by_muscle = {}
        for ex in all_exercises:
            muscle = self._normalize_muscle_group(ex.muscle_group)
            if muscle not in exercises_by_muscle:
                exercises_by_muscle[muscle] = []
            exercises_by_muscle[muscle].append(ex)

        # Сплит-распределение с точными группами для каждого дня
        split_map = {
            3: [
                {"focus": ["грудь", "трицепс"], "muscles": ["грудь", "трицепс"]},
                {"focus": ["спина", "бицепс"], "muscles": ["спина", "бицепс"]},
                {"focus": ["ноги", "плечи"], "muscles": ["ноги", "плечи"]}
            ],
            4: [
                {"focus": ["грудь", "трицепс"], "muscles": ["грудь", "трицепс"]},
                {"focus": ["спина", "бицепс"], "muscles": ["спина", "бицепс"]},
                {"focus": ["ноги", "плечи"], "muscles": ["ноги", "плечи"]},
                {"focus": ["кардио", "пресс"], "muscles": ["кардио", "пресс"]}
            ],
            5: [
                {"focus": ["грудь"], "muscles": ["грудь"]},
                {"focus": ["спина"], "muscles": ["спина"]},
                {"focus": ["ноги"], "muscles": ["ноги"]},
                {"focus": ["плечи", "бицепс", "трицепс"], "muscles": ["плечи", "бицепс", "трицепс"]},
                {"focus": ["кардио", "пресс"], "muscles": ["кардио", "пресс"]}
            ],
            6: [
                {"focus": ["грудь"], "muscles": ["грудь"]},
                {"focus": ["спина"], "muscles": ["спина"]},
                {"focus": ["ноги"], "muscles": ["ноги"]},
                {"focus": ["плечи"], "muscles": ["плечи"]},
                {"focus": ["бицепс"], "muscles": ["бицепс"]},
                {"focus": ["трицепс", "пресс", "кардио"], "muscles": ["трицепс", "пресс", "кардио"]}
            ]
        }

        split = split_map.get(days_per_week, split_map[4])

        # Количество упражнений в день
        if level == "beginner":
            exercises_per_day = 3
        elif level == "intermediate":
            exercises_per_day = 4
        else:
            exercises_per_day = 5

        weekly_plan = []

        for day_idx, day_config in enumerate(split[:days_per_week]):
            day_muscles = day_config["muscles"]
            day_exercises = []
            used_names = set()

            # Добавляем упражнения только из разрешённых групп мышц
            for muscle in day_muscles:
                if muscle not in exercises_by_muscle:
                    continue

                muscle_exercises = exercises_by_muscle[muscle]

                # Фильтр по уровню сложности
                filtered = self._filter_by_level(muscle_exercises, level)

                if not filtered:
                    filtered = muscle_exercises

                # Выбираем уникальное упражнение
                available = [ex for ex in filtered if ex.name not in used_names]
                if not available and filtered:
                    available = filtered

                if available:
                    exercise = random.choice(available)
                    used_names.add(exercise.name)

                    sets_reps = self._calculate_sets_reps(goal, level)

                    day_exercises.append({
                        "name": exercise.name,
                        "muscle_group": self._normalize_muscle_group(exercise.muscle_group),
                        "description": exercise.description or "Нет описания",
                        "sets": sets_reps["sets"],
                        "reps": sets_reps["reps"],
                        "rest_seconds": sets_reps["rest"]
                    })

            # Если не хватает упражнений, добираем из других групп
            if len(day_exercises) < exercises_per_day:
                for muscle in day_muscles:
                    if len(day_exercises) >= exercises_per_day:
                        break
                    if muscle not in exercises_by_muscle:
                        continue

                    available = [ex for ex in exercises_by_muscle[muscle] if ex.name not in used_names]
                    if available:
                        exercise = random.choice(available)
                        sets_reps = self._calculate_sets_reps(goal, level)
                        day_exercises.append({
                            "name": exercise.name,
                            "muscle_group": self._normalize_muscle_group(exercise.muscle_group),
                            "description": exercise.description or "Нет описания",
                            "sets": sets_reps["sets"],
                            "reps": sets_reps["reps"],
                            "rest_seconds": sets_reps["rest"]
                        })
                        used_names.add(exercise.name)

            weekly_plan.append({
                "day": day_idx + 1,
                "exercises": day_exercises,
                "focus": day_config["focus"]
            })

        return {
            "goal": goal,
            "level": level,
            "days_per_week": days_per_week,
            "recommendations": self._get_recommendations(goal, level),
            "weekly_plan": weekly_plan
        }

    def _normalize_muscle_group(self, muscle: str) -> str:
        """Приводим названия групп мышц к единому формату"""
        muscle_lower = muscle.lower()
        mapping = {
            "chest": "грудь",
            "arms": "руки",
            "cardio": "кардио",
            "бицепс": "бицепс",
            "трицепс": "трицепс",
            "пресс": "пресс"
        }
        return mapping.get(muscle_lower, muscle_lower)

    def _filter_by_level(self, exercises: list, level: str) -> list:
        """Фильтрует упражнения по уровню сложности"""
        if level == "beginner":
            return [ex for ex in exercises if ex.difficulty == "beginner"]
        elif level == "intermediate":
            return [ex for ex in exercises if ex.difficulty in ["beginner", "intermediate"]]
        else:
            return exercises

    def _calculate_sets_reps(self, goal: str, level: str) -> Dict[str, int]:
        """Рассчитывает подходы и повторения"""
        if goal == "strength":
            if level == "beginner":
                return {"sets": 3, "reps": 8, "rest": 90}
            elif level == "intermediate":
                return {"sets": 4, "reps": 6, "rest": 120}
            else:
                return {"sets": 4, "reps": 6, "rest": 150}
        elif goal == "endurance":
            if level == "beginner":
                return {"sets": 3, "reps": 12, "rest": 45}
            elif level == "intermediate":
                return {"sets": 3, "reps": 15, "rest": 45}
            else:
                return {"sets": 4, "reps": 20, "rest": 45}
        else:
            if level == "beginner":
                return {"sets": 3, "reps": 10, "rest": 60}
            elif level == "intermediate":
                return {"sets": 3, "reps": 12, "rest": 60}
            else:
                return {"sets": 4, "reps": 10, "rest": 60}

    def _get_recommendations(self, goal: str, level: str) -> List[str]:
        """Рекомендации"""
        base = {
            "strength": ["💪 Поднимай вес 70-85% от максимума", "⏱️ Отдыхай 2-3 минуты"],
            "endurance": ["🏃‍♂️ Используй вес 40-60% от максимума", "⏱️ Отдыхай 30-45 секунд"],
            "balance": ["⚖️ Сочетай силовые и функциональные упражнения", "🧘 Добавь растяжку"]
        }
        level_tips = {
            "beginner": ["🎯 Начинай с 2-3 тренировок в неделю"],
            "intermediate": ["📊 Веди дневник тренировок"],
            "advanced": ["🏋️ Используй дропсеты и суперсеты"]
        }
        result = base.get(goal, base["balance"])
        result.extend(level_tips.get(level, []))
        result.append("🎯 Слушай своё тело!")
        return result

    def _get_fallback_plan(self, goal: str, level: str, days: int) -> Dict[str, Any]:
        """План-заглушка"""
        split = ["грудь+трицепс", "спина+бицепс", "ноги+плечи", "кардио+пресс"]
        weekly_plan = []
        for i in range(min(days, len(split))):
            weekly_plan.append({
                "day": i + 1,
                "exercises": [{"name": "Базовое упражнение", "muscle_group": "общая", "description": "Добавьте упражнения", "sets": 3, "reps": 10, "rest_seconds": 60}],
                "focus": [split[i]]
            })
        return {
            "goal": goal, "level": level, "days_per_week": days,
            "recommendations": ["⚠️ Добавьте упражнения в БД"],
            "weekly_plan": weekly_plan
        }
