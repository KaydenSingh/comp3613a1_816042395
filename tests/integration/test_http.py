from datetime import date

from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.schemas.event import EventCreate
from app.schemas.user import RegularUserCreate
from app.utilities.security import encrypt_password


def seed_user(db, username="bob", role="regular_user"):
    return UserRepository(db).create(
        RegularUserCreate(
            username=username,
            email=f"{username}@example.com",
            password=encrypt_password("bobpass"),
            role=role,
            firstname="Bob",
            lastname="Alumni",
        )
    )


def test_health_endpoint_returns_json(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_users_api_returns_serialized_users(client, db):
    seed_user(db)

    response = client.get("/api/users")

    assert response.status_code == 200
    assert response.json()[0]["username"] == "bob"
    assert "password" not in response.json()[0]


def test_login_sets_cookie_and_opens_authenticated_home(client, db):
    seed_user(db)

    login = client.post(
        "/login",
        data={"username": "bob", "password": "bobpass"},
        follow_redirects=False,
    )

    assert login.status_code == 303
    assert "access_token" in client.cookies

    home = client.get("/app")
    assert home.status_code == 200
    assert "Welcome back, Bob" in home.text


def test_public_search_and_event_detail_show_seeded_event(client, db):
    owner = seed_user(db, username="professor", role="admin")
    event = EventRepository(db).create_for_user(
        EventCreate(
            event_title="Research Showcase",
            description="Poster presentations",
            event_date=date(2026, 11, 12),
            time="10:00 AM",
            location="Science Hall",
            keywords="research",
        ),
        owner.id,
    )

    search = client.get("/search", params={"query": "showcase"})
    detail = client.get(f"/search/events/{event.eventid}")

    assert search.status_code == 200
    assert "Research Showcase" in search.text
    assert detail.status_code == 200
    assert "Bob Alumni" in detail.text


def test_missing_event_detail_returns_not_found(client):
    response = client.get("/search/events/9999")

    assert response.status_code == 404
