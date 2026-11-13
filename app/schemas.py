# app/schemas.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ---------- Users ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ---------- Tasks ----------
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    is_done: bool | None = None

class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    is_done: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)