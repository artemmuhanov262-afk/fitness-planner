#  Fitness Workout Planner API

 REST API для персонализированного планирования тренировок с алгоритмическим генератором планов

##  О проекте

**Fitness Workout Planner** — это backend-сервис, который помогает пользователям создавать индивидуальные планы тренировок на основе их целей, уровня подготовки и доступного времени.

###  Для кого этот проект

- **Для начинающих спортсменов** — кто хочет заниматься, но не знает, с чего начать
- **Для опытных атлетов** — кому нужна система для отслеживания прогресса
- **Для фитнес-тренеров** — желающих автоматизировать создание программ для клиентов
- **Для разработчиков** — как пример чистой архитектуры на FastAPI

###  Возможности

| Функция                      | Описание |
|------------------------------|----------|
|  **Аутентификация**          | Регистрация и вход с JWT-токенами |
|  **Управление упражнениями** | CRUD операции с упражнениями, фильтрация по группам мышц |
|  **Управление тренировками** | CRUD операции с тренировками и подходами (сетами) |
|  **Генерация планов**        | Алгоритмическое создание персонализированных планов тренировок |
|  **Статистика**              | Аналитика тренировок пользователя |
|  **Экспорт**                 | Выгрузка истории тренировок в JSON |
|  **Документация**            | Swagger UI и ReDoc |
|  **Тестирование**            | 24 теста, покрытие 78% |
|  **Качество кода**           | Pylint 9.15/10 |

##  Технологии

| Компонент          | Технология |
|--------------------|------------|
| **Фреймворк**      | FastAPI 0.115.6 |
| **ORM**            | SQLAlchemy 2.0.36 |
| **База данных**    | SQLite (легко заменяется на PostgreSQL) |
| **Аутентификация** | JWT + bcrypt |
| **Валидация**      | Pydantic 2.7.0 |
| **Тестирование**   | Pytest 8.3.4 + pytest-cov 6.0.0 |
| **Качество кода**  | Pylint 3.3.3 |


##  Быстрый старт

### 1 Клонирование
```bash
git clone https://github.com/artemmuhanov262-afk/fitness-planner.git
cd fitness-planner


2 Виртуальное окружение
Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
bash
python3 -m venv venv
source venv/bin/activate


3 Установка зависимостей
bash
pip install -r requirements.txt


4 Запуск сервера
bash
uvicorn app.main:app --reload
Сервер доступен: http://localhost:8000


5 Документация API
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

 API Эндпоинты
 Аутентификация
Метод	Эндпоинт	      Описание
POST	/auth/register	Регистрация
POST	/auth/login	    Вход (JWT)
GET	    /auth/me	    Текущий пользователь

 Упражнения
Метод	Эндпоинт	         Описание
POST	/exercises/	       Создать упражнение
GET	    /exercises/	    Список упражнений
GET	    /exercises/{id}	Получить упражнение
DELETE	/exercises/{id}	Удалить упражнение

 Тренировки
Метод	Эндпоинт	        Описание
POST	/workouts/	      Создать тренировку
GET	    /workouts/	    Список тренировок
GET	    /workouts/{id}	Получить тренировку
PUT	    /workouts/{id}	Обновить тренировку
DELETE	/workouts/{id}	Удалить тренировку

 Подходы (сеты)
Метод	Эндпоинт	                Описание
POST	/workouts/{id}/sets	       Добавить подход
GET	    /workouts/{id}/sets	    Подходы тренировки
DELETE	/workouts/sets/{set_id}	Удалить подход

Генерация плана (БИЗНЕС-ЛОГИКА)
Метод	Эндпоинт	       Описание
POST	/plan/generate	Алгоритмическая генерация плана

Пример запроса:
json
{
  "goal": "strength",
  "days_per_week": 4,
  "level": "intermediate"
}

Параметры:
goal: strength(сила), endurance(выносливость), balance(баланс)
days_per_week: от 3 до 6
level: beginner(начинающий), intermediate(промежуточный), advanced(продвинутый)

 Статистика
Метод	Эндпоинт	            Описание
GET	    /workouts/stats/summary	Статистика тренировок
GET	    /workouts/export/json	Экспорт в JSON

 Тестирование
bash
# Все тесты
pytest app/tests/ -v
# С покрытием
pytest app/tests/ -v --cov=app --cov-report=term-missing
Результат: 24 теста, покрытие 78%

 Качество кода (Pylint)
bash
pylint app --rcfile=.pylintrc
Оценка: 9.15/10


Структура проекта
text
fitness-planner/
├── app/
│   ├── db/              # Настройка БД
│   ├── models/          # SQLAlchemy модели
│   ├── routers/         # API эндпоинты
│   ├── schemas/         # Pydantic схемы
│   ├── services/        # Бизнес-логика
│   │   └── training_planner.py  # Алгоритм 
│   └── tests/           # Тесты (24 шт)
├── requirements.txt
├── .pylintrc
└── README.md


 Алгоритм генерации плана
text
Входные параметры (goal, days_per_week, level)
         ↓
Выбор сплита (какие мышцы в какой день)
         ↓
Расчёт нагрузки (подходы/повторы)
         ↓
Выбор упражнений из БД (случайный, без повторов)
         ↓
Генерация JSON (недельный план)


Автор
Имя: Муханов Артём Александрович
Курс: Программирование на Python
GitHub: https://github.com/artemmuhanov262-afk