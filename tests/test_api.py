import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from dotenv import load_dotenv

from app.main import app
from app.database import SessionLocal, engine, Base
from app.models import User, Permission

load_dotenv()


# Фикстура для создания таблиц перед тестами
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield


# Фикстура для очистки базы данных перед каждым тестом
@pytest.fixture(scope="function", autouse=True)
def clean_db():
    db = SessionLocal()
    try:
        # Очищаем таблицы в правильном порядке (из-за внешних ключей)
        db.execute(text("DELETE FROM permissions"))
        db.execute(text("DELETE FROM tasks"))
        db.execute(text("DELETE FROM users"))
        db.commit()
    finally:
        db.close()


# Фикстура для тестового клиента
@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# Фикстура для получения токена
@pytest.fixture(scope="function")
def auth_token(client: TestClient):
    # Регистрация пользователя
    response = client.post("/register", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 201

    # Авторизация пользователя
    response = client.post("/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    return response.json()["access_token"]


# Фикстура для создания задачи
@pytest.fixture(scope="function")
def created_task(client: TestClient, auth_token: str):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/tasks", json={
        "title": "Test Task",
        "description": "Test Description"
    }, headers=headers)
    assert response.status_code == 201, f"Failed to create task: {response.text}"
    return response.json()


def test_root(client: TestClient):
    """Тест основной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ToDo API is running"}


def test_register_user(client: TestClient):
    """Тест регистрации пользователя"""
    response = client.post("/register", json={
        "username": "newuser",
        "password": "newpassword"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User created"


def test_login_user(client: TestClient):
    """Тест входа пользователя"""
    # Сначала регистрируем
    client.post("/register", json={
        "username": "loginuser",
        "password": "loginpassword"
    })

    # Потом логиним
    response = client.post("/login", json={
        "username": "loginuser",
        "password": "loginpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_create_task(client: TestClient, auth_token: str):
    """Тест создания задачи"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/tasks", json={
        "title": "New Task",
        "description": "Task Description"
    }, headers=headers)

    if response.status_code != 201:
        print(f"Create task failed: {response.status_code} - {response.text}")

    assert response.status_code == 201
    assert response.json()["title"] == "New Task"
    assert response.json()["description"] == "Task Description"
    assert response.json()["completed"] is False


def test_get_tasks(client: TestClient, auth_token: str, created_task: dict):
    """Тест получения задач"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/tasks", headers=headers)

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task"
    assert tasks[0]["id"] == created_task["id"]


def test_update_task(client: TestClient, auth_token: str, created_task: dict):
    """Тест обновления задачи"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_id = created_task["id"]

    response = client.put(f"/tasks/{task_id}", json={
        "title": "Updated Task",
        "description": "Updated Description"
    }, headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["description"] == "Updated Description"


def test_delete_task(client: TestClient, auth_token: str, created_task: dict):
    """Тест удаления задачи"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_id = created_task["id"]

    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"

    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_create_permission(client: TestClient, auth_token: str, created_task: dict):
    """Тест создания прав на задачу"""
    # Создаем второго пользователя
    response = client.post("/register", json={
        "username": "user2",
        "password": "password2"
    })
    assert response.status_code == 201

    # Получаем ID второго пользователя
    with SessionLocal() as db:
        user2 = db.query(User).filter(User.username == "user2").first()

    headers = {"Authorization": f"Bearer {auth_token}"}
    task_id = created_task["id"]

    # Создаем разрешение
    response = client.post("/permissions", json={
        "task_id": task_id,
        "user_id": user2.id,
        "can_edit": True
    }, headers=headers)

    assert response.status_code == 201
    assert response.json()["task_id"] == task_id
    assert response.json()["user_id"] == user2.id
    assert response.json()["can_edit"] is True


def test_shared_task_access(client: TestClient, created_task: dict):
    """Тест наделения прав на задачу"""
    # Создаем второго пользователя
    client.post("/register", json={
        "username": "shared_user",
        "password": "shared_pass"
    })

    # Авторизуем второго пользователя
    login_response = client.post("/login", json={
        "username": "shared_user",
        "password": "shared_pass"
    })
    shared_token = login_response.json()["access_token"]
    shared_headers = {"Authorization": f"Bearer {shared_token}"}

    # Второй пользователь не должен видеть задачу
    response = client.get("/tasks", headers=shared_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

    # Получаем ID второго пользователя
    with SessionLocal() as db:
        user2 = db.query(User).filter(User.username == "shared_user").first()

    # Создаем разрешение от первого пользователя
    auth_response = client.post("/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert auth_response.status_code == 200, "Failed to login as owner"
    owner_token = auth_response.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    perm_response = client.post("/permissions", json={
        "task_id": created_task["id"],
        "user_id": user2.id,
        "can_edit": True
    }, headers=owner_headers)
    assert perm_response.status_code == 201, "Failed to create permission"


def test_delete_permission(client: TestClient, auth_token: str):
    """Тест удаления прав на задачу"""
    # Создаем второго пользователя
    client.post("/register", json={
        "username": "perm_user",
        "password": "perm_pass"
    })

    # Получаем ID второго пользователя
    with SessionLocal() as db:
        user2 = db.query(User).filter(User.username == "perm_user").first()

    # Создаем задачу
    headers = {"Authorization": f"Bearer {auth_token}"}
    task_response = client.post("/tasks", json={
        "title": "Permission Task",
        "description": "Permission Description"
    }, headers=headers)
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    # Создаем разрешение
    perm_response = client.post("/permissions", json={
        "task_id": task_id,
        "user_id": user2.id,
        "can_edit": True
    }, headers=headers)
    assert perm_response.status_code == 201
    permission_id = perm_response.json()["id"]

    # Удаляем разрешение
    response = client.delete(f"/permissions/{permission_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Права отозваны"

    # Проверяем, что разрешение удалено
    with SessionLocal() as db:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        assert permission is None
