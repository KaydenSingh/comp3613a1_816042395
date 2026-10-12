from app.repositories.event import EventRepository
from app.schemas.event import EventCreate


class EventService:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def create_event(self, payload: EventCreate, user_id: int):
        return self.event_repo.create_for_user(payload, user_id)

    def list_my_events(self, user_id: int):
        return self.event_repo.list_by_user(user_id)

    def search_events(self, query: str):
        return self.event_repo.search_events(query)

    def get_event_details(self, eventid: int):
        # --- STUDENT SNIPPET: EVENT DETAILS ---
        event = self.event_repo.get_by_id(eventid)
        hosts = self.event_repo.get_hosts(eventid)
        return event, hosts
        # --- END STUDENT SNIPPET ---
