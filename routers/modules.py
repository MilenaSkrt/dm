from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Module, User
from pydantic import BaseModel

router = APIRouter(prefix="/modules", tags=["modules"])

# Pydantic модели
class ModuleCreate(BaseModel):
    title: str
    description: str
    teacher_id: int  # ID преподавателя

# Создать модуль
@router.post("/")
def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
    teacher = db.query(User).filter(User.id == module.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")

    new_module = Module(
        title=module.title,
        description=module.description,
        teacher_id=module.teacher_id
    )
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return {"message": "Модуль создан", "module_id": new_module.id}

# Получить все модули
@router.get("/")
def get_modules(db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    return modules