from __future__ import annotations

from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role: str = "regular_user"
    firstname: str = Field(default="")
    lastname: str = Field(default="")
    yeargraduated: Optional[int] = Field(default=None)
    department: str = Field(default="")
    profile_description: str = Field(default="")
    connection_ids: str = Field(default="")


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    @property
    def full_name(self) -> str:
        name = " ".join(part for part in (self.firstname, self.lastname) if part).strip()
        return name or self.username
