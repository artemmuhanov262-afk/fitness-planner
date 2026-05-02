from fastapi import FastAPI
from app.db.database import Base, engine
from app.routers import auth, workouts, exercises, planner, admin

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fitness Workout Planner API",
    description="API для планирования тренировок с алгоритмическим генератором планов",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(workouts.router)
app.include_router(exercises.router)
app.include_router(planner.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Fitness Planner API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
