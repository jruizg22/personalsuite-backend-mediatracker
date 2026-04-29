from typing import Callable, Generator, Any

from fastapi import APIRouter
from sqlmodel import Session

from .media import get_router as media_router
from .tools import router as tools_router
from .youtube import get_router as youtube_router

def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/v1",
    )

    router.include_router(media_router(get_session))
    router.include_router(youtube_router(get_session))
    router.include_router(tools_router)

    return router