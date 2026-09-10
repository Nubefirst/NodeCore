from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from backend.app.core.enums import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)



class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    role:  UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)