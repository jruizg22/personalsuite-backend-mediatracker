from typing import Callable, Generator, Any

from fastapi import APIRouter
from sqlmodel import Session

from .yt_channel_controller import get_router as yt_channel_router

def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/youtube",
    )

    router.include_router(yt_channel_router(get_session))

    return router