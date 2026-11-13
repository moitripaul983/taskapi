# app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas
from app.security import hash_password


# ---------- Users ----------
def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.UserCreate) -> models.User:
    user = models.User(
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------- Tasks ----------
def create_task(db: Session, data: schemas.TaskCreate, owner_id: int) -> models.Task:
    task = models.Task(**data.model_dump(), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 20,
    is_done: bool | None = None,
) -> list[models.Task]:
    query = db.query(models.Task).filter(models.Task.owner_id == owner_id)
    if is_done is not None:
        query = query.filter(models.Task.is_done == is_done)
    return query.order_by(models.Task.id).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int, owner_id: int) -> models.Task | None:
    return (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == owner_id)
        .first()
    )


def update_task(db: Session, task: models.Task, data: schemas.TaskUpdate) -> models.Task:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    db.delete(task)
    db.commit()