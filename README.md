# ToDo API with Shared Tasks

REST API приложение для управления задачами с возможностью совместного доступа, построенное на FastAPI и PostgreSQL.

## 🌟 Основные возможности

- 🔐 Регистрация и аутентификация пользователей (JWT)
- ✅ Создание, чтение, обновление и удаление задач
- 🤝 Совместный доступ к задачам с разными уровнями прав
- 🔑 Управление разрешениями для других пользователей
- 🧪 Полностью покрыто тестами

## 🛠 Технологический стек

- **Backend**: Python, FastAPI
- **База данных**: PostgreSQL
- **Аутентификация**: JWT (JSON Web Tokens)
- **Хеширование паролей**: Bcrypt
- **ORM**: SQLAlchemy
- **Валидация**: Pydantic
- **Тестирование**: Pytest, TestClient

## Установка 

1. Клонировать репозиторий и установить зависимости:
    ```bash
    git clone https://github.com/Ivanmatv/todo_list.git
    cd todo_list
    ```
2. Создайте виртуальное окружение и установите зависимости:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/MacOS
    source venv\Scripts\activate     # Windows
    pip install -r requirements.txt
    ```
3. Создайте файл .env в корне проекта:
    ```bash
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=todo_db
    ```
4. Также можно запустить при помощи Dockerfile:

    ```bash
    docker build -t todo-app .
    ```



## Примеры запросов
### Документация по запросам
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

1. Регистрация пользователя
    ```bash
    POST http://127.0.0.1:8000/register
    Content-Type: application/json

    {
        "username": "user1",
        "password": "password1"
    }
    ```
    Ответ
    ```bash
    HTTP/1.1 201 Created
    Content-Type: application/json

    {
        "message": "User created"
    }
    ```
2. Авторизация
    ```bash
    POST http://127.0.0.1:8000/login
    Content-Type: application/json

    {
        "username": "user1",
        "password": "password1"
    }
    ```
    Ответ
    ```bash
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
3. Создание задачи
    ```bash
    POST http://127.0.0.1:8000/tasks
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    Content-Type: application/json

    {
        "title": "Купить молоко",
        "description": "Не забыть купить молоко вечером"
    }
    ```
    Ответ
    ```bash
    HTTP/1.1 201 Created
    Content-Type: application/json

    {
        "id": 1,
        "title": "Купить молоко",
        "description": "Не забыть купить молоко вечером",
        "completed": false,
        "owner_id": 1
    }
    ```
4. Получение списка задач
    ```bash
    GET http://127.0.0.1:8000/tasks
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    Ответ
    ```bash
    HTTP/1.1 200 OK
    Content-Type: application/json

    [
        {
            "id": 1,
            "title": "Купить молоко",
            "description": "Не забыть купить молоко вечером",
            "completed": false,
            "owner_id": 1
        },
        ...
    ]
    ```
5. Обновление задачи
    ```bash
    PUT http://127.0.0.1:8000/tasks/{task_id}
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    Content-Type: application/json

    {
        "title": "Купить молоко и хлеб",
        "description": "Купить молоко и хлеб вечером"
    }
    ```
    Ответ
    ```bash
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "id": 1,
        "title": "Купить молоко и хлеб",
        "description": "Купить молоко и хлеб вечером",
        "completed": false,
        "owner_id": 1
    }
    ```
6. Удаление задачи
    ```bash
    DELETE http://127.0.0.1:8000/tasks/{task_id}
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    Ответ
    ```bash
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "message": "Task deleted"
    }
    ```
7. Предоставление прав доступа на задачу
    ```bash
    POST http://127.0.0.1:8000/permissions
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    Content-Type: application/json

    {
        "task_id": 1,
        "user_id": 2,
        "can_edit": true
    }
    ```
    Ответ
    ```bash
    HTTP/1.1 201 Created
    Content-Type: application/json

    {
        "id": 1,
        "task_id": 1,
        "user_id": 2,
        "can_edit": true
    }
    ```
8. Отзыв прав доступа
    ```bash
    DELETE http://127.0.0.1:8000/permissions/{permission_id}
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    Ответ
    ```bash
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "message": "Права отозваны"
    }
    ```

## Проведение тестов API

- python -m pytest tests/test_api.py -v

Должен выйти результат


![Результаты выполнения тестов](images/test-results.png)

