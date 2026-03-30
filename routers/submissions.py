from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Submission, Task, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/submissions", tags=["submissions"])

# Pydantic модель
class SubmissionCreate(BaseModel):
    student_id: int
    task_id: int
    code: str
    score: int | None = None  # Можно ставить преподавателем позже

# Сдать задание (студент)
@router.post("/")
def create_submission(sub: SubmissionCreate, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.id == sub.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    task = db.query(Task).filter(Task.id == sub.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    new_sub = Submission(
        student_id=sub.student_id,
        task_id=sub.task_id,
        code=sub.code,
        score=sub.score,
        submitted_at=datetime.utcnow()
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return {"message": "Задание сдано", "submission_id": new_sub.id}

# Получить все сдачи студента
@router.get("/student/{student_id}")
def get_student_submissions(student_id: int, db: Session = Depends(get_db)):
    submissions = db.query(Submission).filter(Submission.student_id == student_id).all()
    return submissions

# Получить все сдачи по заданию (для преподавателя)
@router.get("/task/{task_id}")
def get_task_submissions(task_id: int, db: Session = Depends(get_db)):
    submissions = db.query(Submission).filter(Submission.task_id == task_id).all()
    return submissions