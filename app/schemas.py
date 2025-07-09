from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str
    description: str = ""


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    owner_id: int


class PermissionCreate(BaseModel):
    task_id: int
    user_id: int
    can_edit: bool
