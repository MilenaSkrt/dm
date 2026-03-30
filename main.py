from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal, engine, Base
from models import Role, Group, User, Module, Task, Submission
from schemas import (
    UserCreate, UserRead, UserUpdate,
    RoleCreate, RoleRead, RoleUpdate,
    GroupCreate, GroupRead, GroupUpdate,
    ModuleCreate, ModuleRead, ModuleUpdate,
    TaskCreate, TaskRead, TaskUpdate,
    SubmissionCreate, SubmissionRead, SubmissionUpdate
)

app = FastAPI(title="Study M API", description="API для системы Study M", version="1.0")

# Создание всех таблиц в БД
Base.metadata.create_all(bind=engine)


# ---------------- DB Session ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "study_m system работает"}


# ---------------- CRUD HELPERS ----------------
def get_object_or_404(db, model, object_id, detail="Object not found"):
    obj = db.query(model).filter(model.id == object_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=detail)
    return obj


# ------------------- USERS -------------------
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(**user.dict(), status="active")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, User, user_id, "User not found")


@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = get_object_or_404(db, User, user_id, "User not found")
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = get_object_or_404(db, User, user_id, "User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


# ------------------- ROLES -------------------
@app.post("/roles/")
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    new_role = Role(
        name=role.name
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@app.get("/roles/", response_model=List[RoleRead])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@app.get("/roles/{role_id}", response_model=RoleRead)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Role, role_id, "Role not found")


@app.put("/roles/{role_id}", response_model=RoleRead)
def update_role(role_id: int, role_update: RoleUpdate, db: Session = Depends(get_db)):
    role = get_object_or_404(db, Role, role_id, "Role not found")
    for key, value in role_update.dict(exclude_unset=True).items():
        setattr(role, key, value)
    db.commit()
    db.refresh(role)
    return role


@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = get_object_or_404(db, Role, role_id, "Role not found")
    db.delete(role)
    db.commit()
    return {"detail": "Role deleted"}


# ------------------- GROUPS -------------------
@app.post("/groups/", response_model=GroupRead)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    new_group = Group(**group.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group


@app.get("/groups/", response_model=List[GroupRead])
def get_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()


@app.get("/groups/{group_id}", response_model=GroupRead)
def get_group(group_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Group, group_id, "Group not found")


@app.put("/groups/{group_id}", response_model=GroupRead)
def update_group(group_id: int, group_update: GroupUpdate, db: Session = Depends(get_db)):
    group = get_object_or_404(db, Group, group_id, "Group not found")
    for key, value in group_update.dict(exclude_unset=True).items():
        setattr(group, key, value)
    db.commit()
    db.refresh(group)
    return group


@app.delete("/groups/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = get_object_or_404(db, Group, group_id, "Group not found")
    db.delete(group)
    db.commit()
    return {"detail": "Group deleted"}


# ------------------- MODULES -------------------
@app.post("/modules/", response_model=ModuleRead)
def create_module(module: ModuleCreate, db: Session = Depends(get_db)):
    new_module = Module(**module.dict())
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module


@app.get("/modules/", response_model=List[ModuleRead])
def get_modules(db: Session = Depends(get_db)):
    return db.query(Module).all()


@app.get("/modules/{module_id}", response_model=ModuleRead)
def get_module(module_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Module, module_id, "Module not found")


@app.put("/modules/{module_id}", response_model=ModuleRead)
def update_module(module_id: int, module_update: ModuleUpdate, db: Session = Depends(get_db)):
    module = get_object_or_404(db, Module, module_id, "Module not found")
    for key, value in module_update.dict(exclude_unset=True).items():
        setattr(module, key, value)
    db.commit()
    db.refresh(module)
    return module


@app.delete("/modules/{module_id}")
def delete_module(module_id: int, db: Session = Depends(get_db)):
    module = get_object_or_404(db, Module, module_id, "Module not found")
    db.delete(module)
    db.commit()
    return {"detail": "Module deleted"}


# ------------------- TASKS -------------------
@app.post("/tasks/", response_model=TaskRead)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(**task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks/", response_model=List[TaskRead])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Task, task_id, "Task not found")


@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = get_object_or_404(db, Task, task_id, "Task not found")
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = get_object_or_404(db, Task, task_id, "Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}


# ------------------- SUBMISSIONS -------------------
@app.post("/submissions/", response_model=SubmissionRead)
def create_submission(submission: SubmissionCreate, db: Session = Depends(get_db)):
    new_submission = Submission(**submission.dict())
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission


@app.get("/submissions/", response_model=List[SubmissionRead])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(Submission).all()


@app.get("/submissions/{submission_id}", response_model=SubmissionRead)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    return get_object_or_404(db, Submission, submission_id, "Submission not found")


@app.put("/submissions/{submission_id}", response_model=SubmissionRead)
def update_submission(submission_id: int, submission_update: SubmissionUpdate, db: Session = Depends(get_db)):
    submission = get_object_or_404(db, Submission, submission_id, "Submission not found")
    for key, value in submission_update.dict(exclude_unset=True).items():
        setattr(submission, key, value)
    db.commit()
    db.refresh(submission)
    return submission


@app.delete("/submissions/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = get_object_or_404(db, Submission, submission_id, "Submission not found")
    db.delete(submission)
    db.commit()
    return {"detail": "Submission deleted"}