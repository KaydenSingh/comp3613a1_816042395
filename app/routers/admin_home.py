from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep, IsUserLoggedIn, get_current_user, is_admin
from app.repositories.event import EventRepository
from app.services.event_service import EventService
from app.schemas.event import EventCreate
from app.utilities.flash import flash
from . import router, templates


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db:SessionDep
):
    event_service = EventService(EventRepository(db))
    my_events = event_service.list_my_events(user.id)
    return templates.TemplateResponse(
        request=request, 
        name="admin.html",
        context={
            "user": user,
            "events": my_events,
        }
    )


@router.post("/admin/events/create")
async def create_admin_event(
    request: Request,
    user: AdminDep,
    db: SessionDep,
    event_title: str = Form(...),
    description: str = Form(""),
    event_date: str = Form(...),
    time: str = Form(...),
    location: str = Form(...),
    keywords: str = Form(""),
):
    event_service = EventService(EventRepository(db))
    payload = EventCreate(
        event_title=event_title,
        description=description or None,
        event_date=event_date,
        time=time,
        location=location,
        keywords=keywords,
    )

    # STUDENT ROUTE SNIPPET: replace this block with one thin service call.
    created_event = event_service.create_event(payload, user.id)

    flash(request, f"Event '{created_event.event_title}' created", "success")
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
