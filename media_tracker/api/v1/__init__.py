from typing import Callable, Generator, Any

from fastapi import APIRouter
from sqlmodel import Session

from .media_controller import get_router as media_router
from .media_translation_controller import get_router as media_translation_router


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/v1",
    )

    router.include_router(media_router(get_session))
    router.include_router(media_translation_router(get_session))

    return router