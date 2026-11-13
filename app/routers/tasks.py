# app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_owned_task_or_404(db: Session, task_id: int, user: models.User) -> models.Task:
    task = crud.get_task(db, task_id, user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.create_task(db, data, user.id)


@router.get("", response_model=list[schemas.TaskOut])
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_done: bool | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return crud.list_tasks(db, user.id, skip, limit, is_done)


@router.get("/{task_id}", response_model=schemas.TaskOut)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return _get_owned_task_or_404(db, task_id, user)


@router.patch("/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    task = _get_owned_task_or_404(db, task_id, user)
    return crud.update_task(db, task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    task = _get_owned_task_or_404(db, task_id, user)
    crud.delete_task(db, task)