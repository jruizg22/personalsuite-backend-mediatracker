from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from media_tracker.models.yt import YTChannelPublic
from media_tracker.services import yt_channel_service


def get_router(get_session) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_model=list[YTChannelPublic])
    def get_all(session: Session = Depends(get_session)) -> list[YTChannelPublic]:
        try:
            return yt_channel_service.get_all(session)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube channels: {e}"))

    return router