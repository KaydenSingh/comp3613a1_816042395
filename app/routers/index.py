from fastapi import HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.services.event_service import EventService
from app.services.user_service import UserService
from app.utilities.flash import flash
from . import router, templates


async def _public_nav(request: Request, user_logged_in: bool, db):
    dashboard_url = request.url_for("login_view")
    connections_url = request.url_for("login_view")
    if user_logged_in:
        user = await get_current_user(request, db)
        dashboard_url = (
            request.url_for("admin_home_view")
            if await is_admin(user)
            else request.url_for("user_home_view")
        )
        connections_url = request.url_for("connections_list_view")
    return dashboard_url, connections_url


@router.get("/", response_class=HTMLResponse, name="index_view")
async def index_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep,
):
    app_home = request.url_for("login_view")
    if user_logged_in:
        user = await get_current_user(request, db)
        if await is_admin(user):
            app_home = request.url_for("admin_home_view")
        else:
            app_home = request.url_for("user_home_view")

    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            "user_logged_in": user_logged_in,
            "app_home": app_home,
        },
    )


@router.get("/search", response_class=HTMLResponse, name="search_view")
async def search_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep,
    query: str = "",
):
    event_service = EventService(EventRepository(db))
    events = event_service.search_events(query)
    dashboard_url, connections_url = await _public_nav(request, user_logged_in, db)

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "user_logged_in": user_logged_in,
            "query": query,
            "events": events,
            "dashboard_url": dashboard_url,
            "connections_url": connections_url,
        },
    )


@router.get("/search/events/{eventid}", response_class=HTMLResponse, name="event_detail_view")
async def event_detail_view(
    request: Request,
    eventid: int,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep,
):
    # --- STUDENT SNIPPET: VIEW EVENT DETAILS ---
    event_service = EventService(EventRepository(db))
    event, hosts = event_service.get_event_details(eventid)
    # --- END STUDENT SNIPPET ---

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    dashboard_url, connections_url = await _public_nav(request, user_logged_in, db)

    return templates.TemplateResponse(
        request=request,
        name="event_detail.html",
        context={
            "user_logged_in": user_logged_in,
            "event": event,
            "hosts": hosts,
            "dashboard_url": dashboard_url,
            "connections_url": connections_url,
        },
    )


@router.get("/profiles/{user_id}", response_class=HTMLResponse, name="professor_profile_view")
async def professor_profile_view(
    request: Request,
    user_id: int,
    user: AuthDep,
    db: SessionDep,
):
    user_service = UserService(UserRepository(db))
    profile = user_service.get_user_by_id(user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    connected_ids = {item.id for item in user_service.get_connections(user.id)}
    return templates.TemplateResponse(
        request=request,
        name="professor_profile.html",
        context={
            "user": user,
            "profile": profile,
            "is_self": user.id == profile.id,
            "already_connected": profile.id in connected_ids,
        },
    )


@router.post("/profiles/{user_id}/connect", name="connect_profile")
async def connect_profile(
    request: Request,
    user_id: int,
    user: AuthDep,
    db: SessionDep,
):
    user_service = UserService(UserRepository(db))
    try:
        user_service.connect_users(user.id, user_id)
        flash(request, "Connection added.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for("professor_profile_view", user_id=user_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/profiles/{user_id}/disconnect", name="disconnect_profile")
async def disconnect_profile(
    request: Request,
    user_id: int,
    user: AuthDep,
    db: SessionDep,
):
    user_service = UserService(UserRepository(db))
    try:
        user_service.disconnect_users(user.id, user_id)
        flash(request, "Connection removed.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for("professor_profile_view", user_id=user_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/connections", response_class=HTMLResponse, name="connections_list_view")
async def connections_list_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep,
):
    user_service = UserService(UserRepository(db))
    dashboard_url, connections_url = await _public_nav(request, user_logged_in, db)

    current_user_connection_ids = set()
    users = []
    if user_logged_in:
        try:
            user = await get_current_user(request, db)
            connections = user_service.get_connections(user.id)
            users = connections
            current_user_connection_ids = {item.id for item in connections}
        except Exception:
            users = []
            current_user_connection_ids = set()
    else:
        users = []

    return templates.TemplateResponse(
        request=request,
        name="connections.html",
        context={
            "user_logged_in": user_logged_in,
            "users": users,
            "dashboard_url": dashboard_url,
            "connections_url": connections_url,
            "current_user_connection_ids": current_user_connection_ids,
        },
    )
