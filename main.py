from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

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
from auth import hash_password, verify_password, create_access_token, get_current_user
from routers import sandbox

# ---------------- APP ----------------
app = FastAPI(title="Study M API")

app.include_router(sandbox.router)

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------- LOGIN ----------------
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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

# ==================== CRUD ПОЛЬЗОВАТЕЛИ ====================
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user.dict(exclude={"password"}), password=hash_password(user.password), status="active")
    db.add(new_user); db.commit(); db.refresh(new_user)
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
        setattr(user, key, hash_password(value) if key == "password" else value)
    db.commit(); db.refresh(user)
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = get_object_or_404(db, User, user_id)
    db.delete(user); db.commit()
    return {"detail": "deleted"}

# ==================== CRUD РОЛИ ====================
@app.post("/roles/", response_model=RoleRead)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    r = Role(**role.dict()); db.add(r); db.commit(); db.refresh(r); return r

@app.get("/roles/", response_model=List[RoleRead])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@app.get("/roles/{role_id}", response_model=RoleRead)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Role, role_id)

@app.put("/roles/{role_id}", response_model=RoleRead)
def update_role(role_id: int, data: RoleUpdate, db: Session = Depends(get_db)):
    role = get_object_or_404(db, Role, role_id)
    for k, v in data.dict(exclude_unset=True).items(): setattr(role, k, v)
    db.commit(); db.refresh(role); return role

@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = get_object_or_404(db, Role, role_id)
    db.delete(role); db.commit(); return {"detail": "deleted"}

# ==================== CRUD ГРУППЫ ====================
@app.post("/groups/", response_model=GroupRead)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    g = Group(**group.dict()); db.add(g); db.commit(); db.refresh(g); return g

@app.get("/groups/", response_model=List[GroupRead])
def get_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()

@app.get("/groups/{group_id}", response_model=GroupRead)
def get_group(group_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Group, group_id)

@app.put("/groups/{group_id}", response_model=GroupRead)
def update_group(group_id: int, data: GroupUpdate, db: Session = Depends(get_db)):
    g = get_object_or_404(db, Group, group_id)
    for k, v in data.dict(exclude_unset=True).items(): setattr(g, k, v)
    db.commit(); db.refresh(g); return g

@app.delete("/groups/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    g = get_object_or_404(db, Group, group_id)
    db.delete(g); db.commit(); return {"detail": "deleted"}

# ==================== CRUD МОДУЛИ ====================
@app.post("/modules/", response_model=ModuleRead)
def create_module(module: ModuleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    m = Module(**module.dict()); db.add(m); db.commit(); db.refresh(m); return m

@app.get("/modules/", response_model=List[ModuleRead])
def get_modules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Module).all()

@app.get("/modules/{id}", response_model=ModuleRead)
def get_module(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_object_or_404(db, Module, id)

@app.put("/modules/{id}", response_model=ModuleRead)
def update_module(id: int, data: ModuleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    m = get_object_or_404(db, Module, id)
    for k, v in data.dict(exclude_unset=True).items(): setattr(m, k, v)
    db.commit(); db.refresh(m); return m

@app.delete("/modules/{id}")
def delete_module(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    m = get_object_or_404(db, Module, id)
    db.delete(m); db.commit(); return {"detail": "deleted"}

# ==================== CRUD ЗАДАНИЯ ====================
@app.post("/tasks/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = Task(**task.dict()); db.add(t); db.commit(); db.refresh(t); return t

@app.get("/tasks/", response_model=List[TaskRead])
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).all()

@app.get("/tasks/{id}", response_model=TaskRead)
def get_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_object_or_404(db, Task, id)

@app.put("/tasks/{id}", response_model=TaskRead)
def update_task(id: int, data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = get_object_or_404(db, Task, id)
    for k, v in data.dict(exclude_unset=True).items(): setattr(t, k, v)
    db.commit(); db.refresh(t); return t

@app.delete("/tasks/{id}")
def delete_task(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    t = get_object_or_404(db, Task, id)
    db.delete(t); db.commit(); return {"detail": "deleted"}

# ==================== CRUD ОТПРАВКИ ====================
@app.post("/submissions/", response_model=SubmissionRead)
def create_submission(sub: SubmissionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    s = Submission(**sub.dict(), user_id=current_user.id)
    db.add(s); db.commit(); db.refresh(s); return s

@app.get("/submissions/", response_model=List[SubmissionRead])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(Submission).all()

@app.get("/submissions/{id}", response_model=SubmissionRead)
def get_submission(id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Submission, id)

@app.put("/submissions/{id}", response_model=SubmissionRead)
def update_submission(id: int, data: SubmissionUpdate, db: Session = Depends(get_db)):
    s = get_object_or_404(db, Submission, id)
    for k, v in data.dict(exclude_unset=True).items(): setattr(s, k, v)
    db.commit(); db.refresh(s); return s

@app.delete("/submissions/{id}")
def delete_submission(id: int, db: Session = Depends(get_db)):
    s = get_object_or_404(db, Submission, id)
    db.delete(s); db.commit(); return {"detail": "deleted"}

# ==================== СТРАНИЦЫ ====================
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login_page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/theory")
def theory_page(request: Request):
    return templates.TemplateResponse("theory.html", {"request": request})

@app.get("/physics")
def physics_page(request: Request):
    return templates.TemplateResponse("physics.html", {"request": request})

@app.get("/optimization")
def optimization_page(request: Request):
    return templates.TemplateResponse("optimization.html", {"request": request})

@app.get("/modules_page")
def modules_page(request: Request, db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    return templates.TemplateResponse("modules.html", {"request": request, "modules": modules})

@app.get("/tasks_page")
def tasks_page(request: Request, db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})

@app.get("/submit/{task_id}")
def submit_page(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return templates.TemplateResponse("submit_task.html", {"request": request, "task": task})

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)