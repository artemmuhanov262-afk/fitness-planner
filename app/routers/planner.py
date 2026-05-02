from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.routers.auth import get_current_user
from app.models.models import User
from app.services.training_planner import TrainingPlanner

router = APIRouter(prefix="/plan", tags=["Training Plan"])


class PlanRequest(BaseModel):
    """Запрос на генерацию плана тренировок."""
    goal: str = Field(
        ...,
        description="Цель: strength (сила), endurance (выносливость), balance (баланс)"
    )
    days_per_week: int = Field(
        ...,
        ge=3,
        le=6,
        description="Количество тренировок в неделю (3-6)"
    )
    level: str = Field(
        ...,
        description="Уровень: beginner, intermediate, advanced"
    )


class ExerciseInPlan(BaseModel):
    """Упражнение в плане тренировок."""
    name: str
    muscle_group: str
    description: Optional[str]
    sets: int
    reps: int
    rest_seconds: int


class PlanDay(BaseModel):
    """День тренировки в плане."""
    day: int
    exercises: List[ExerciseInPlan]


class PlanResponse(BaseModel):
    """Ответ с планом тренировок."""
    goal: str
    level: str
    days_per_week: int
    recommendations: List[str]
    weekly_plan: List[PlanDay]


@router.post("/generate", response_model=PlanResponse)
def generate_training_plan(
    request: PlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Генерирует оптимальный план тренировок на неделю.

    Алгоритм учитывает:
    - Уровень подготовки пользователя (beginner/intermediate/advanced)
    - Цель тренировок (strength/endurance/balance)
    - Оптимальное распределение нагрузки по дням
    - Расчёт подходов и повторений на основе научных рекомендаций

    Это НЕ CRUD операция, а полноценный алгоритмический компонент.
    """
    # Валидация входных данных
    valid_goals = ["strength", "endurance", "balance"]
    if request.goal not in valid_goals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Goal must be one of: {', '.join(valid_goals)}"
        )

    if request.days_per_week < 3 or request.days_per_week > 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days per week must be between 3 and 6"
        )

    valid_levels = ["beginner", "intermediate", "advanced"]
    if request.level not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Level must be one of: {', '.join(valid_levels)}"
        )

    # Генерируем план
    try:
        planner = TrainingPlanner(db)
        plan = planner.generate_plan(
            goal=request.goal,
            days_per_week=request.days_per_week,
            level=request.level
        )
        return PlanResponse(**plan)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating plan: {str(e)}"
        ) from e
