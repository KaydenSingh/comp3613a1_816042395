from app.models.user import UserBase
from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    yeargraduated: Optional[int] = None
    department: Optional[str] = None
    profile_description: Optional[str] = None
    connection_ids: Optional[str] = None


class AdminCreate(UserBase):
    role: str = "admin"


class RegularUserCreate(UserBase):
    role: str = "regular_user"


class UserResponse(SQLModel):
    id: int
    username: str
    email: EmailStr
    role: str = "regular_user"
    firstname: str = ""
    lastname: str = ""
    department: str = ""
    yeargraduated: int | None = None
    profile_description: str = ""


class SignupRequest(SQLModel):
    username: str
    email: EmailStr
    password: str
