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
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

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

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
    PDF_FONT = "DejaVu"
else:
    PDF_FONT = "Helvetica"

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
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
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


@app.get("/roles/{role_id}", response_model=RoleRead)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Role, role_id)


@app.put("/roles/{role_id}", response_model=RoleRead)
def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    role = get_object_or_404(db, Role, role_id)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(role, k, v)
    db.commit()
    db.refresh(role)
    return role


@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = get_object_or_404(db, Role, role_id)
    db.delete(role)
    db.commit()
    return {"detail": "deleted"}


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


@app.get("/groups/{group_id}", response_model=GroupRead)
def get_group(group_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Group, group_id)


@app.put("/groups/{group_id}", response_model=GroupRead)
def update_group(group_id: int, data: GroupUpdate, db: Session = Depends(get_db)):
    g = get_object_or_404(db, Group, group_id)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(g, k, v)
    db.commit()
    db.refresh(g)
    return g


@app.delete("/groups/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    g = get_object_or_404(db, Group, group_id)
    db.delete(g)
    db.commit()
    return {"detail": "deleted"}


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


@app.get("/modules/{id}", response_model=ModuleRead)
def get_module(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_object_or_404(db, Module, id)


@app.put("/modules/{id}", response_model=ModuleRead)
def update_module(id: int, data: ModuleUpdate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    m = get_object_or_404(db, Module, id)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m


@app.delete("/modules/{id}")
def delete_module(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    m = get_object_or_404(db, Module, id)
    db.delete(m)
    db.commit()
    return {"detail": "deleted"}


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


@app.get("/tasks/{id}", response_model=TaskRead)
def get_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_object_or_404(db, Task, id)


@app.put("/tasks/{id}", response_model=TaskRead)
def update_task(id: int, data: TaskUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    t = get_object_or_404(db, Task, id)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


@app.delete("/tasks/{id}")
def delete_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = get_object_or_404(db, Task, id)
    db.delete(t)
    db.commit()
    return {"detail": "deleted"}


# ---------------- SUBMISSIONS ----------------
@app.post("/submissions/", response_model=SubmissionRead)
def create_submission(sub: SubmissionCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    s = Submission(**sub.dict(), user_id=current_user.id)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@app.get("/submissions/", response_model=List[SubmissionRead])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(Submission).all()


@app.get("/submissions/{id}", response_model=SubmissionRead)
def get_submission(id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Submission, id)


@app.put("/submissions/{id}", response_model=SubmissionRead)
def update_submission(id: int, data: SubmissionUpdate, db: Session = Depends(get_db)):
    s = get_object_or_404(db, Submission, id)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@app.delete("/submissions/{id}")
def delete_submission(id: int, db: Session = Depends(get_db)):
    s = get_object_or_404(db, Submission, id)
    db.delete(s)
    db.commit()
    return {"detail": "deleted"}


# ================ ОТЧЁТЫ (5 штук) ================

# 1. ОТЧЁТ ПО ПОЛЬЗОВАТЕЛЯМ
@app.get("/report/users/pdf")
def report_users_pdf(db: Session = Depends(get_db)):
    users = db.query(User).all()
    file = "users_report.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 16)
    c.drawString(200, 820, "ОТЧЕТ №1: ПОЛЬЗОВАТЕЛИ")
    c.setFont(PDF_FONT, 10)
    c.drawString(50, 800, f"Дата формирования: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.drawString(50, 785, f"Всего пользователей: {len(users)}")

    c.setFont(PDF_FONT, 12)
    y = 750

    for u in users:
        c.drawString(50, y, f"{u.id} | {u.full_name} | {u.email} | {u.status}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file, media_type='application/pdf', filename="users_report.pdf")


# 2. ОТЧЁТ ПО ЗАДАНИЯМ
@app.get("/report/tasks/pdf")
def report_tasks_pdf(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    file = "tasks_report.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 16)
    c.drawString(200, 820, "ОТЧЕТ №2: ЗАДАНИЯ")
    c.setFont(PDF_FONT, 10)
    c.drawString(50, 800, f"Дата формирования: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.drawString(50, 785, f"Всего заданий: {len(tasks)}")

    c.setFont(PDF_FONT, 12)
    y = 750

    for t in tasks:
        desc = (t.description[:50] + '...') if len(t.description) > 50 else t.description
        c.drawString(50, y, f"{t.id} | {t.title} | {desc}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file, media_type='application/pdf', filename="tasks_report.pdf")


# 3. ОТЧЁТ ПО ОТПРАВКАМ (С ОЦЕНКАМИ)
@app.get("/report/submissions/pdf")
def report_submissions_pdf(db: Session = Depends(get_db)):
    subs = db.query(Submission).all()
    file = "submissions_report.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 16)
    c.drawString(200, 820, "ОТЧЕТ №3: ОТПРАВКИ ЗАДАНИЙ")
    c.setFont(PDF_FONT, 10)
    c.drawString(50, 800, f"Дата формирования: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.drawString(50, 785, f"Всего отправок: {len(subs)}")

    # Подсчёт средней оценки
    grades = [s.grade for s in subs if s.grade is not None]
    avg_grade = sum(grades) / len(grades) if grades else 0

    c.drawString(50, 770, f"Средняя оценка: {avg_grade:.2f}")

    c.setFont(PDF_FONT, 12)
    y = 740

    for s in subs:
        c.drawString(50, y, f"{s.id} | Задание:{s.task_id} | Студент:{s.user_id} | Оценка:{s.grade or 'не проверено'}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file, media_type='application/pdf', filename="submissions_report.pdf")


# 4. ОТЧЁТ ПО МОДУЛЯМ И СТАТИСТИКА ЗАДАНИЙ
@app.get("/report/modules/pdf")
def report_modules_pdf(db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    tasks = db.query(Task).all()
    file = "modules_report.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 16)
    c.drawString(180, 820, "ОТЧЕТ №4: МОДУЛИ И СТАТИСТИКА")
    c.setFont(PDF_FONT, 10)
    c.drawString(50, 800, f"Дата формирования: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}")
    c.drawString(50, 785, f"Всего модулей: {len(modules)}")
    c.drawString(50, 770, f"Всего заданий: {len(tasks)}")

    c.setFont(PDF_FONT, 12)
    y = 740

    for m in modules:
        tasks_in_module = [t for t in tasks if t.module_id == m.id]
        c.drawString(50, y, f"Модуль: {m.title} | Заданий: {len(tasks_in_module)}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file, media_type='application/pdf', filename="modules_report.pdf")


# 5. СВОДНЫЙ ОТЧЁТ ПО УСПЕВАЕМОСТИ
@app.get("/report/performance/pdf")
def report_performance_pdf(db: Session = Depends(get_db)):
    users = db.query(User).all()
    submissions = db.query(Submission).all()
    tasks = db.query(Task).all()
    file = "performance_report.pdf"
    c = canvas.Canvas(file, pagesize=A4)

    c.setFont(PDF_FONT, 16)
    c.drawString(150, 820, "ОТЧЕТ №5: СВОДНЫЙ ПО УСПЕВАЕМОСТИ")
    c.setFont(PDF_FONT, 10)
    c.drawString(50, 800, f"Дата формирования: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}")

    c.setFont(PDF_FONT, 12)
    y = 770

    for u in users:
        user_subs = [s for s in submissions if s.user_id == u.id]
        completed = len(user_subs)
        avg_grade = sum([s.grade for s in user_subs if s.grade]) / len(user_subs) if user_subs else 0

        c.drawString(50, y, f"{u.full_name} | Выполнено: {completed}/{len(tasks)} | Средний балл: {avg_grade:.2f}")
        y -= 20
        if y < 50:
            c.showPage()
            c.setFont(PDF_FONT, 12)
            y = 800

    c.save()
    return FileResponse(file, media_type='application/pdf', filename="performance_report.pdf")