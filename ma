from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from database import SessionLocal, Base, engine
from models import Role, Group, User, Module, Task, Submission
from schemas import (
    UserCreate, UserRead, UserUpdate,
    RoleCreate, RoleRead, RoleUpdate,
    GroupCreate, GroupRead, GroupUpdate,
    ModuleCreate, ModuleRead, ModuleUpdate,
    TaskCreate, TaskRead, TaskUpdate,
    SubmissionCreate, SubmissionRead, SubmissionUpdate
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

# ---------------- FONT ----------------
FONT_PATH = "DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
PDF_FONT = "DejaVu"

# ---------------- APP ----------------
app = FastAPI(title="Study M API")
Base.metadata.create_all(bind=engine)

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- LOGIN ----------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Wrong password")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# ---------------- HELPER ----------------
def get_object_or_404(db, model, object_id):
    obj = db.query(model).filter(model.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

# ---------------- USERS ----------------
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        **user.dict(exclude={"password"}),
        password=hash_password(user.password),
        status="active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).all()

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_object_or_404(db, User, user_id)

@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_object_or_404(db, User, user_id)

    for key, value in data.dict(exclude_unset=True).items():
        if key == "password":
            setattr(user, key, hash_password(value))
        else:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_object_or_404(db, User, user_id)
    db.delete(user)
    db.commit()
    return {"detail": "deleted"}

# ---------------- ROLES ----------------
@app.post("/roles/", response_model=RoleRead)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    r = Role(**role.dict())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@app.get("/roles/", response_model=List[RoleRead])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

# ---------------- GROUPS ----------------
@app.post("/groups/", response_model=GroupRead)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    g = Group(**group.dict())
    db.add(g)
    db.commit()
    db.refresh(g)
    return g

@app.get("/groups/", response_model=List[GroupRead])
def get_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()

# ---------------- MODULES ----------------
@app.post("/modules/", response_model=ModuleRead)
def create_module(module: ModuleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    m = Module(**module.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@app.get("/modules/", response_model=List[ModuleRead])
def get_modules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Module).all()

# ---------------- TASKS ----------------
@app.post("/tasks/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = Task(**task.dict())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@app.get("/tasks/", response_model=List[TaskRead])
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).all()

# ---------------- SUBMISSIONS ----------------
@app.post("/submissions/", response_model=SubmissionRead)
def create_submission(sub: SubmissionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    s = Submission(**sub.dict(), user_id=current_user.id)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@app.get("/submissions/", response_model=List[SubmissionRead])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(Submission).all()

# ---------------- PDF USERS ----------------
@app.get("/report/users/pdf")
def report_users_pdf(db: Session = Depends(get_db)):
    users = db.query(User).all()
    file = "users.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 12)
    y = 800

    c.drawString(200, y, "Отчет по пользователям")
    y -= 40

    for u in users:
        c.drawString(50, y, f"{u.id} | {u.full_name} | {u.email}")
        y -= 20

        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file)

# ---------------- PDF TASKS ----------------
@app.get("/report/tasks/pdf")
def report_tasks_pdf(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    file = "tasks.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 12)
    y = 800

    c.drawString(200, y, "Отчет по заданиям")
    y -= 40

    for t in tasks:
        c.drawString(50, y, f"{t.id} | {t.title}")
        y -= 20

        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file)

# ---------------- PDF SUBMISSIONS ----------------
@app.get("/report/submissions/pdf")
def report_submissions_pdf(db: Session = Depends(get_db)):
    subs = db.query(Submission).all()
    file = "subs.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 12)
    y = 800

    c.drawString(200, y, "Отчет по отправкам")
    y -= 40

    for s in subs:
        c.drawString(50, y, f"{s.id} | task:{s.task_id} | user:{s.user_id} | grade:{s.grade}")
        y -= 20

        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file)
