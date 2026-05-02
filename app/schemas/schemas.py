from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# USER SCHEMAS
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# AUTH SCHEMAS
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

#  EXERCISE SCHEMAS
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

# SET LOG SCHEMAS
class SetLogBase(BaseModel):
    exercise_id: int
    reps: int = Field(..., ge=1)
    weight: float = Field(0.0, ge=0)
    order_number: int

class SetLogCreate(SetLogBase):
    pass

class SetLogResponse(SetLogBase):
    id: int
    workout_id: int

    class Config:
        from_attributes = True

# WORKOUT SCHEMAS
class WorkoutBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1)

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1)

class WorkoutResponse(WorkoutBase):
    id: int
    date: datetime
    user_id: int
    sets: List[SetLogResponse] = []

    class Config:
        from_attributes = True
