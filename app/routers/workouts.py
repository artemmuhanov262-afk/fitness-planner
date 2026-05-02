from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.models.models import User, Workout, Exercise, SetLog
from app.routers.auth import get_current_user

class WorkoutBase(BaseModel):
    """Базовая схема тренировки."""
    title: str = Field(..., min_length=1, max_length=100, description="Название тренировки")
    description: Optional[str] = Field(None, description="Описание тренировки")
    duration_minutes: Optional[int] = Field(None, ge=1, le=480, description="Длительность в минутах")

class WorkoutCreate(WorkoutBase):
    """Схема для создания тренировки."""

class WorkoutUpdate(BaseModel):
    """Схема для обновления тренировки."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=480)

# СХЕМЫ ДЛЯ ПОДХОДОВ

class SetLogBase(BaseModel):
    """Базовая схема подхода."""
    exercise_id: int = Field(..., description="ID упражнения")
    reps: int = Field(..., ge=1, le=100, description="Количество повторений")
    weight: float = Field(0.0, ge=0, le=500, description="Вес в кг")
    order_number: int = Field(..., ge=1, description="Порядковый номер упражнения")

class SetLogCreate(SetLogBase):
    """Схема для создания подхода."""

class SetLogResponse(SetLogBase):
    """Схема ответа с подходом."""
    id: int
    workout_id: int

    class Config:
        from_attributes = True

class WorkoutResponse(WorkoutBase):
    """Схема ответа с тренировкой."""
    id: int
    date: datetime
    user_id: int
    sets: List[SetLogResponse] = []

    class Config:
        from_attributes = True

# СОЗДАНИЕ РОУТЕРА

router = APIRouter(prefix="/workouts", tags=["Workouts"])


# CRUD ДЛЯ ТРЕНИРОВОК

@router.post("/", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новую тренировку.

    - **title**: Название тренировки (обязательно)
    - **description**: Описание (необязательно)
    - **duration_minutes**: Длительность в минутах (необязательно)
    """
    db_workout = Workout(
        title=workout.title,
        description=workout.description,
        duration_minutes=workout.duration_minutes,
        user_id=current_user.id
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@router.get("/", response_model=List[WorkoutResponse])
def get_workouts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список всех тренировок пользователя.

    - **skip**: Количество пропущенных записей (пагинация)
    - **limit**: Максимальное количество записей
    """
    workouts = db.query(Workout).filter(
        Workout.user_id == current_user.id
    ).order_by(Workout.date.desc()).offset(skip).limit(limit).all()
    return workouts


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить тренировку по ID.
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена"
        )
    return workout


@router.put("/{workout_id}", response_model=WorkoutResponse)
def update_workout(
    workout_id: int,
    workout_update: WorkoutUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить тренировку.

    Можно обновить любое из полей: title, description, duration_minutes.
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена"
        )

    # Обновляем только переданные поля
    update_data = workout_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workout, field, value)

    db.commit()
    db.refresh(workout)
    return workout


@router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить тренировку.
    """
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена"
        )

    db.delete(workout)
    db.commit()


# РАБОТА С ПОДХОДАМИ (СЕТАМИ)

@router.post("/{workout_id}/sets", response_model=SetLogResponse, status_code=status.HTTP_201_CREATED)
def add_set_to_workout(
    workout_id: int,
    set_log: SetLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Добавить подход (сет) к тренировке.

    - **exercise_id**: ID упражнения из базы
    - **reps**: Количество повторений (1-100)
    - **weight**: Вес в кг (0-500)
    - **order_number**: Порядковый номер упражнения в тренировке
    """
    # Проверяем, существует ли тренировка и принадлежит ли пользователю
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена"
        )

    # Проверяем, существует ли упражнение
    exercise = db.query(Exercise).filter(Exercise.id == set_log.exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Упражнение не найдено"
        )

    db_set = SetLog(
        workout_id=workout_id,
        exercise_id=set_log.exercise_id,
        reps=set_log.reps,
        weight=set_log.weight,
        order_number=set_log.order_number
    )
    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    return db_set


@router.get("/{workout_id}/sets", response_model=List[SetLogResponse])
def get_workout_sets(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить все подходы тренировки.
    """
    # Проверяем доступ к тренировке
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена"
        )

    sets = db.query(SetLog).filter(
        SetLog.workout_id == workout_id
    ).order_by(SetLog.order_number).all()
    return sets


@router.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(
    set_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить подход из тренировки.
    """
    set_log = db.query(SetLog).filter(SetLog.id == set_id).first()

    if not set_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подход не найден"
        )

    # Проверяем, принадлежит ли тренировка пользователю
    workout = db.query(Workout).filter(
        Workout.id == set_log.workout_id,
        Workout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому подходу"
        )

    db.delete(set_log)
    db.commit()

# СТАТИСТИКА И АНАЛИТИКА

@router.get("/stats/summary")
def get_workout_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить статистику тренировок пользователя.

    Возвращает:
    - total_workouts: общее количество тренировок
    - total_duration_minutes: суммарная длительность
    - average_duration_minutes: средняя длительность
    - total_exercises: общее количество выполненных упражнений
    - workouts_per_week: среднее количество тренировок в неделю
    """
    workouts = db.query(Workout).filter(Workout.user_id == current_user.id).all()

    if not workouts:
        return {
            "total_workouts": 0,
            "total_duration_minutes": 0,
            "average_duration_minutes": 0,
            "total_exercises": 0,
            "workouts_per_week": 0,
            "message": "У вас пока нет тренировок"
        }

    total_duration = sum(w.duration_minutes or 0 for w in workouts)
    avg_duration = total_duration // len(workouts) if workouts else 0

    # Подсчёт упражнений
    total_exercises = 0
    for workout in workouts:
        sets_count = db.query(SetLog).filter(SetLog.workout_id == workout.id).count()
        total_exercises += sets_count

    return {
        "total_workouts": len(workouts),
        "total_duration_minutes": total_duration,
        "average_duration_minutes": avg_duration,
        "total_exercises": total_exercises,
        "workouts_per_week": round(len(workouts) / 4, 1)
    }


# ЭКСПОРТ ТРЕНИРОВОК

@router.get("/export/json")
def export_workouts_json(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Экспортировать все тренировки в JSON формате.

    Удобно для сохранения истории тренировок или импорта в другие приложения.
    """
    workouts = db.query(Workout).filter(Workout.user_id == current_user.id).all()

    result = []
    for workout in workouts:
        sets = db.query(SetLog).filter(SetLog.workout_id == workout.id).all()
        result.append({
            "id": workout.id,
            "title": workout.title,
            "description": workout.description,
            "date": workout.date.isoformat(),
            "duration_minutes": workout.duration_minutes,
            "sets": [
                {
                    "exercise_id": s.exercise_id,
                    "reps": s.reps,
                    "weight": s.weight,
                    "order_number": s.order_number
                }
                for s in sets
            ]
        })

    return {
        "user": current_user.username,
        "total_workouts": len(result),
        "workouts": result
    }
