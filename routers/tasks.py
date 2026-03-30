from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Task, Module
from pydantic import BaseModel

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Pydantic модели
class TaskCreate(BaseModel):
    title: str
    description: str
    max_score: int
    module_id: int

# Создать задание
@router.post("/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == task.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Модуль не найден")

    new_task = Task(
        title=task.title,
        description=task.description,
        max_score=task.max_score,
        module_id=task.module_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Задание создано", "task_id": new_task.id}

# Получить все задания
@router.get("/")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks