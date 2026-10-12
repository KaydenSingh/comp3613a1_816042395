from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    eventid: Optional[int] = Field(default=None, primary_key=True)
    event_title: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    event_date: str
    time: str
    location: str
    userid: Optional[int] = Field(default=None, foreign_key="user.id")
    keywords: str


class EventHost(SQLModel, table=True):
    # --- STUDENT SNIPPET: EVENT_HOST ---
    # Complete these two columns so they match EVENT_HOST on the ERD.
    eventid: Optional[int] = Field(default=None, foreign_key="event.eventid", primary_key=True)
    userid: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    # --- END STUDENT SNIPPET ---