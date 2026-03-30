from pydantic import BaseModel
from typing import Optional

# ---------------- USER ----------------
class UserCreate(BaseModel):
    full_name: str
    email: str  # раньше EmailStr
    password: str
    role_id: int
    group_id: int

class UserRead(BaseModel):
    id: int
    full_name: str
    email: str  # раньше EmailStr
    role_id: int
    group_id: int
    status: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[str]  # раньше EmailStr
    password: Optional[str]
    role_id: Optional[int]
    group_id: Optional[int]
    status: Optional[str]


# ---------------- ROLE ----------------
class RoleCreate(BaseModel):
    name: str

class RoleRead(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class RoleUpdate(BaseModel):
    name: Optional[str]


# ---------------- GROUP ----------------
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class GroupRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

class GroupUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


# ---------------- MODULE ----------------
class ModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ModuleRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None

    class Config:
        orm_mode = True

class ModuleUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]


# ---------------- TASK ----------------
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    module_id: int

class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    module_id: int

    class Config:
        orm_mode = True

class TaskUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    module_id: Optional[int]


# ---------------- SUBMISSION ----------------
class SubmissionCreate(BaseModel):
    user_id: int
    task_id: int
    content: str
    grade: Optional[float] = None

class SubmissionRead(BaseModel):
    id: int
    user_id: int
    task_id: int
    content: str
    grade: Optional[float] = None

    class Config:
        orm_mode = True

class SubmissionUpdate(BaseModel):
    content: Optional[str]
    grade: Optional[float]
    user_id: Optional[int]
    task_id: Optional[int]