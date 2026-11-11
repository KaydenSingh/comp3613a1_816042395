from datetime import date

import pytest

from app.models.user import User
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.schemas.event import EventCreate
from app.schemas.user import RegularUserCreate
from app.services.auth_service import AuthService
from app.utilities.security import encrypt_password


def test_event_create_strips_required_fields():
    payload = EventCreate(
        event_title="  Alumni Mixer  ",
        event_date=date(2026, 11, 10),
        time="  6:00 PM ",
        location="  Main Hall ",
    )

    assert payload.event_title == "Alumni Mixer"
    assert payload.time == "6:00 PM"
    assert payload.location == "Main Hall"


def test_event_create_rejects_blank_required_fields():
    with pytest.raises(ValueError, match="This field is required"):
        EventCreate(
            event_title=" ",
            event_date=date(2026, 11, 10),
            time="6:00 PM",
            location="Main Hall",
        )


def test_auth_service_registers_and_authenticates_user(db):
    service = AuthService(UserRepository(db))

    created = service.register_user(
        "alumni-one",
        "alumni-one@example.com",
        "secret-pass",
    )

    assert created.username == "alumni-one"
    assert created.password != "secret-pass"
    assert service.authenticate_user("alumni-one", "secret-pass")
    assert service.authenticate_user("alumni-one", "wrong-pass") is None


def test_user_repository_connections_are_idempotent_and_removable(db):
    repository = UserRepository(db)
    first = repository.create(
        RegularUserCreate(
            username="first",
            email="first@example.com",
            password=encrypt_password("password"),
        )
    )
    second = repository.create(
        RegularUserCreate(
            username="second",
            email="second@example.com",
            password=encrypt_password("password"),
        )
    )

    repository.connect_users(first.id, second.id)
    repository.connect_users(first.id, second.id)
    assert [user.id for user in repository.get_connections(first.id)] == [second.id]

    repository.disconnect_users(first.id, second.id)
    assert repository.get_connections(first.id) == []

    with pytest.raises(ValueError, match="cannot connect"):
        repository.connect_users(first.id, first.id)


def test_event_repository_search_matches_title_and_location(db):
    repository = EventRepository(db)
    owner = User(
        username="event-owner",
        email="event-owner@example.com",
        password=encrypt_password("password"),
        role="admin",
    )
    db.add(owner)
    db.commit()
    db.refresh(owner)

    repository.create_for_user(
        EventCreate(
            event_title="Research Showcase",
            event_date=date(2026, 11, 12),
            time="10:00 AM",
            location="Science Hall",
            keywords="posters",
        ),
        owner.id,
    )

    assert [event.event_title for event in repository.search_events("showcase")] == [
        "Research Showcase"
    ]
    assert [event.event_title for event in repository.search_events("science")] == [
        "Research Showcase"
    ]
