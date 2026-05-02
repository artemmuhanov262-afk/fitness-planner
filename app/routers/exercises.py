from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.database import get_db
from app.models.models import User, Exercise
from app.routers.auth import get_current_user

# Временные схемы
class ExerciseBase(BaseModel):
    name: str
    muscle_group: str
    difficulty: str
    description: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int

    class Config:
        from_attributes = True

router = APIRouter(prefix="/exercises", tags=["Exercises"])

@router.post("/", response_model=ExerciseResponse)
def create_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка существующего упражнения
    db_exercise = db.query(Exercise).filter(Exercise.name == exercise.name).first()
    if db_exercise:
        raise HTTPException(status_code=400, detail="Exercise already exists")

    db_exercise = Exercise(**exercise.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

@router.get("/", response_model=List[ExerciseResponse])
def get_exercises(
    skip: int = 0,
    limit: int = 100,
    muscle_group: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Exercise)
    if muscle_group:
        query = query.filter(Exercise.muscle_group == muscle_group)
    exercises = query.offset(skip).limit(limit).all()
    return exercises

@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

# НОВЫЙ DELETE ЭНДПОИНТ
@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление упражнения по ID.
    Требуется авторизация.
    """
    # Находим упражнение
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found"
        )

    # Сохраняем имя для сообщения
    exercise_name = exercise.name

    # Удаляем
    db.delete(exercise)
    db.commit()

    return {
        "message": f"Exercise '{exercise_name}' (id: {exercise_id}) deleted successfully",
        "deleted_id": exercise_id,
        "deleted_name": exercise_name
    }
