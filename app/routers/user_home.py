from fastapi import Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.user import UserRepository
from app.services.user_service import UserService
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    connections = user_service.get_connections(user.id)

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "connections": connections,
            "connection_count": len(connections),
        },
    )