from typing import Callable, Generator, Any

from fastapi import APIRouter
from sqlmodel import Session

from .v1 import get_router as v1_get_router


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/api",
    )

    router.include_router(v1_get_router(get_session))

    return router