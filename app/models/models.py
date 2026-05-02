from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)  # Полное имя
    is_active = Column(Integer, default=1)  # 1 = активен, 0 = неактивен
    created_at = Column(DateTime, default=datetime.utcnow)  # Дата регистрации

    # Связи
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # Название тренировки
    description = Column(Text)  # Описание
    date = Column(DateTime, default=datetime.utcnow)  # Дата проведения
    duration_minutes = Column(Integer)  # Длительность в минутах
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Связи
    user = relationship("User", back_populates="workouts")
    sets = relationship("SetLog", back_populates="workout", cascade="all, delete-orphan")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # Название упражнения
    muscle_group = Column(String)  # Группа мышц: грудь, спина, ноги, плечи, руки, кардио
    difficulty = Column(String)    # Сложность: новичок, средний, продвинутый
    description = Column(Text)     # Описание

    # Связи
    sets = relationship("SetLog", back_populates="exercise")


class SetLog(Base):
    __tablename__ = "set_logs"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    reps = Column(Integer, nullable=False)  # Количество повторений
    weight = Column(Float, default=0.0)    # Вес в кг
    order_number = Column(Integer)         # Порядковый номер

    # Связи
    workout = relationship("Workout", back_populates="sets")
    exercise = relationship("Exercise", back_populates="sets")
