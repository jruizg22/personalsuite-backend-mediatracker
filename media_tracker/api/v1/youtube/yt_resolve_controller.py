from fastapi import APIRouter, Depends, HTTPException, Query

from media_tracker.integrations.youtube.providers.ytdlp_client import YTDLPClient
from media_tracker.integrations.youtube.providers.ytdlp_provider import YTDLPProvider
from media_tracker.models.yt_resolve import (
    YTResolvedVideo
)
from media_tracker.services.youtube.yt_resolver_service import YTResolverService

router = APIRouter(
    prefix="/resolve",
    tags=["YouTube Resolve"]
)

def get_service() -> YTResolverService:
    client = YTDLPClient()
    provider = YTDLPProvider(client)
    return YTResolverService(provider)

@router.post("/video", response_model=YTResolvedVideo, status_code=200)
def resolve_video(
    url: str = Query(..., description="YouTube video URL"),
    service: YTResolverService = Depends(get_service)
) -> YTResolvedVideo:

    try:
        return service.resolve_video(url)

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