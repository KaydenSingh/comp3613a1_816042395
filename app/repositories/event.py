from sqlmodel import Session, select, or_

from app.models.event import Event, EventHost
from app.models.user import User
from app.schemas.event import EventCreate


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_for_user(self, payload: EventCreate, user_id: int) -> Event:
        event = Event(
            event_title=payload.event_title,
            description=payload.description,
            event_date=str(payload.event_date),
            time=payload.time,
            location=payload.location,
            keywords=payload.keywords,
            userid=user_id,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        if event.eventid and user_id:
            self.db.add(EventHost(eventid=event.eventid, userid=user_id))
            self.db.commit()
        return event

    def list_by_user(self, user_id: int) -> list[Event]:
        statement = select(Event).where(Event.userid == user_id).order_by(Event.event_date.desc())
        return list(self.db.exec(statement).all())

    def search_events(self, query: str) -> list[Event]:
        text = (query or "").strip()
        if not text:
            statement = select(Event).order_by(Event.event_date.desc())
            return list(self.db.exec(statement).all())

        like = f"%{text}%"
        statement = (
            select(Event)
            .where(
                or_(
                    Event.event_title.ilike(like),
                    Event.location.ilike(like),
                    Event.keywords.ilike(like),
                    Event.description.ilike(like),
                )
            )
            .order_by(Event.event_date.desc())
        )
        return list(self.db.exec(statement).all())

    def get_by_id(self, eventid: int):
        # --- STUDENT SNIPPET: LOAD EVENT ---
        statement= select(Event).where(Event.eventid == eventid)
        return self.db.exec(statement).first()
        # --- END STUDENT SNIPPET ---

    def get_hosts(self, eventid: int):
        # --- STUDENT SNIPPET: LOAD HOSTS ---
        statement = (
            select(User)
            .join(EventHost, EventHost.userid == User.id)
            .where(EventHost.eventid == eventid)
        )
        hosts = list(self.db.exec(statement).all())
        if hosts:
            return hosts
        event = self.get_by_id(eventid)
        if event and event.userid:
            fallback = self.db.get(User, event.userid)
            return [fallback] if fallback else []
        return []
        # --- END STUDENT SNIPPET ---
