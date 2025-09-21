from typing import Callable, Generator, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from media_tracker.models.yt import YTChannelPublic
from media_tracker.services.youtube import yt_channel_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/channels",
        tags=["YouTube Channels"]
    )

    @router.get("/", response_model=list[YTChannelPublic])
    def get_all_yv_channels(session: Session = Depends(get_session)) -> list[YTChannelPublic]:
        try:
            return yt_channel_service.get_all(session)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube channels: {e}"))

    return router