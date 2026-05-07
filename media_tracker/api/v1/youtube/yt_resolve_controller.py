from fastapi import APIRouter, Depends, HTTPException, Query

from media_tracker.dependencies.service import get_yt_resolver_service
from media_tracker.models.yt_resolve import (
    YTResolvedVideo, YTResolvedChannel
)
from media_tracker.services.youtube.yt_resolver_service import YTResolverService

router = APIRouter(
    prefix="/resolve",
    tags=["YouTube Resolve"]
)

@router.get("/channel", response_model=YTResolvedChannel, status_code=200)
def resolve_channel(
    url: str | None = Query(
        None,
        description="YouTube channel URL (optional)"
    ),
    channel_id: str | None = Query(
        None,
        description="Canonical YouTube channel ID (UC...)"
    ),
    service: YTResolverService = Depends(get_yt_resolver_service)
) -> YTResolvedChannel:
    try:
        return service.resolve_channel(url, channel_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/video", response_model=YTResolvedVideo, status_code=200)
def resolve_video(
    url: str = Query(
        ...,
        description="YouTube video URL"
    ),
    rich_channel: bool = Query(
        False,
        description="Whether to enrich channel metadata"
    ),
    service: YTResolverService = Depends(get_yt_resolver_service)
) -> YTResolvedVideo:
    try:
        return service.resolve_video(url, rich_channel)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )