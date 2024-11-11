from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class UserBase(BaseModel):
    name: str
    email: EmailStr
    mobile: Optional[str] = None
    username: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    username: Optional[str] = None

class User(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
