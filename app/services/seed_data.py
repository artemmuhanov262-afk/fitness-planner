from sqlalchemy.orm import Session
from app.models.models import Exercise

def seed_exercises(db: Session):
    """Добавляет тестовые упражнения в базу данных"""

    exercises = [
        # Грудные
        Exercise(name="Жим штанги лёжа", muscle_group="грудь", difficulty="intermediate", description="Классическое базовое упражнение для груди"),
        Exercise(name="Отжимания от пола", muscle_group="грудь", difficulty="beginner", description="Базовое упражнение с собственным весом"),
        Exercise(name="Жим гантелей на наклонной", muscle_group="грудь", difficulty="intermediate", description="Прорабатывает верх груди"),

        # Спина
        Exercise(name="Подтягивания", muscle_group="спина", difficulty="advanced", description="Широкий хват"),
        Exercise(name="Тяга штанги в наклоне", muscle_group="спина", difficulty="intermediate", description="Для толщины спины"),
        Exercise(name="Горизонтальная тяга", muscle_group="спина", difficulty="beginner", description="В тренажёре"),

        # Ноги
        Exercise(name="Приседания со штангой", muscle_group="ноги", difficulty="intermediate", description="Базовое упражнение для ног"),
        Exercise(name="Выпады с гантелями", muscle_group="ноги", difficulty="beginner", description="Хорошо для ягодиц"),
        Exercise(name="Становая тяга", muscle_group="ноги", difficulty="advanced", description="Базовое упражнение"),

        # Плечи
        Exercise(name="Жим штанги стоя", muscle_group="плечи", difficulty="intermediate", description="Армейский жим"),
        Exercise(name="Разведение гантелей в стороны", muscle_group="плечи", difficulty="beginner", description="Для средней дельты"),

        # Руки
        Exercise(name="Подъём штанги на бицепс", muscle_group="руки", difficulty="beginner", description="Стоя"),
        Exercise(name="Французский жим", muscle_group="руки", difficulty="intermediate", description="Для трицепса"),

        # Кардио
        Exercise(name="Бег", muscle_group="кардио", difficulty="beginner", description="На беговой дорожке или улице"),
        Exercise(name="Скакалка", muscle_group="кардио", difficulty="beginner", description="Отличное кардио"),
        Exercise(name="Интервальный спринт", muscle_group="кардио", difficulty="advanced", description="30 сек работа / 30 сек отдых"),

        # Пресс
        Exercise(name="Скручивания", muscle_group="пресс", difficulty="beginner", description="На полу"),
        Exercise(name="Планка", muscle_group="пресс", difficulty="beginner", description="Держать 30-60 секунд"),
        Exercise(name="Подъём ног в висе", muscle_group="пресс", difficulty="advanced", description="На турнике"),
    ]

    for exercise in exercises:
        existing = db.query(Exercise).filter(Exercise.name == exercise.name).first()
        if not existing:
            db.add(exercise)

    db.commit()
    print(f"✅ Добавлено {len(exercises)} упражнений в базу данных")
