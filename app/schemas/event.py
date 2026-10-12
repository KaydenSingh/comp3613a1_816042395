from datetime import date

from pydantic import field_validator
from sqlmodel import SQLModel


class EventCreate(SQLModel):
    event_title: str
    description: str | None = None
    event_date: date
    time: str
    location: str
    keywords: str = ""

    @field_validator("event_title", "time", "location")
    @classmethod
    def strip_required(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("This field is required")
        return clean


class EventResponse(SQLModel):
    eventid: int
    event_title: str
    description: str | None
    event_date: date
    time: str
    location: str
    keywords: str
    userid: int | None
