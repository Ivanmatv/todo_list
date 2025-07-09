from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager

from .models import Task, Base, User, Permission
from .schemas import UserCreate, UserLogin, TaskCreate, PermissionCreate
from .crud import (
    create_task,
    get_task,
    update_task,
    delete_task,
    create_user,
    get_user,
    get_permission,
    create_permission,
    delete_permission
)
from .auth import decode_token, verify_password, create_access_token
from .database import SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            db_version = result.scalar()
            print(f"✅ Подключение к PostgreSQL успешно. Версия: {db_version}")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        import sys
        sys.exit(1)

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        user = get_user(db, username=username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}"
        )


@app.get("/")
def read_root():
    return {"message": "ToDo API is running"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user(db, user.username):
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже есть")
    create_user(db, user)
    return {"message": "User created"}


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user(db, user.username)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Недействительные данные")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/tasks", status_code=201)
def create_task_endpoint(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_task(db, task, current_user.id)


@app.get("/tasks")
def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    own_tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()

    shared_tasks = db.query(Task).join(Permission).filter(
        Permission.user_id == current_user.id
    ).all()

    return own_tasks + shared_tasks


@app.put("/tasks/{task_id}")
def update_task_endpoint(
    task_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.owner_id != current_user.id:
        permission = get_permission(db, task_id, current_user.id)
        if not permission or not permission.can_edit:
            raise HTTPException(status_code=403, detail="Нет прав на редактирование")

    return update_task(db, task_id, task_data.model_dump())


@app.delete("/tasks/{task_id}")
def delete_task_endpoitn(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_task(db, task_id)
    if task and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может удалить")

    if not delete_task(db, task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"message": "Task deleted"}


@app.post("/permissions", status_code=status.HTTP_201_CREATED)
def create_permission_endpoint(
    permission: PermissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_task(db, permission.task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может предоставить права")

    return create_permission(db, permission)


@app.delete("/permissions/{permission_id}")
def delete_permission_endpoint(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    permission = db.get(Permission, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Права не найдены")

    task = get_task(db, permission.task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только владелец может отзвать права")

    delete_permission(db, permission_id)
    return {"message": "Права отозваны"}
