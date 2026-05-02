"""Admin endpoints for database management."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.routers.auth import get_current_user
from app.models.models import User
from app.services.seed_data import seed_exercises

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/seed-exercises")
def seed_exercises_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # noqa: ARG001
):
    """Добавляет тестовые упражнения в БД (только для админа)."""
    seed_exercises(db)
    return {"message": "Exercises added successfully"}
