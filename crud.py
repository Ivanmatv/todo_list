from sqlalchemy.orm import Session

from auth import get_password_hash
import models, schemas


def get_task(db: Session, task_id: int):
    """Функция для получения задачи по ID"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def create_task(db: Session, task: schemas.TaskCreate):
    """Функция для создания новой задачи"""
    db_task = models.Task(title=task.title, description=task.description, completed=task.completed)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task_data: dict):
    """Функция обновления задачи"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id)
    db_task.update(task_data)
    db.commit()
    return db_task.first()


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
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    """Функция создания пользователя"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_permission(db: Session, permission: schemas.PermissionCreate):
    """Функция создания прав доступа"""
    db_permission = models.Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def get_permission(db: Session, task_id: int, user_id: int):
    """Функция получения прав доступа"""
    return db.query(models.Permission).filter(
        models.Permission.task_id == task_id,
        models.Permission.user_id == user_id
    ).first()


def delete_permission(db: Session, permission_id: int):
    """Функция удаления прав доступа"""
    permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if permission:
        db.delete(permission)
        db.commit()
        return True
    return False
