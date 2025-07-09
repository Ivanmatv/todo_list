from sqlalchemy.orm import Session

from .auth import get_password_hash
from .models import Task, User, Permission
from .schemas import TaskCreate, UserCreate, PermissionCreate


def get_task(db: Session, task_id: int):
    """Функция для получения задачи по ID"""
    return db.query(Task).filter(Task.id == task_id).first()


def create_task(db: Session, task: TaskCreate, owner_id: int):
    """Функция для создания новой задачи"""
    db_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed if hasattr(task, 'completed') else False,
        owner_id=owner_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_data: dict):
    """Функция обновления задачи"""
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None

    for key, value in task_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    """Функция для удаления задачи по ID"""
    db_task = get_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return db_task
    return None


def get_user(db: Session, username: str):
    """Функция получения пользователя по имени"""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    """Функция создания пользователя"""
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_permission(db: Session, permission: PermissionCreate):
    """Функция создания прав доступа"""
    db_permission = Permission(
        task_id=permission.task_id,
        user_id=permission.user_id,
        can_edit=permission.can_edit
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def get_permission(db: Session, task_id: int, user_id: int):
    """Функция получения прав доступа"""
    return db.query(Permission).filter(
        Permission.task_id == task_id,
        Permission.user_id == user_id
    ).first()


def delete_permission(db: Session, permission_id: int):
    """Функция удаления прав доступа"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if permission:
        db.delete(permission)
        db.commit()
        return True
    return False
