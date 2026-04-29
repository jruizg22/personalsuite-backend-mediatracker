from fastapi import APIRouter, HTTPException

from media_tracker.models.ytdlp import YTDLPUpdateResult, YTDLPStatus
from media_tracker.tools.ytdlp.exceptions import YTDLPUpdateAlreadyRunningError, YTDLPAlreadyUpToDateError
from media_tracker.tools.ytdlp.ytdlp_management import get_status
from media_tracker.tools.ytdlp.ytdlp_update_service import update_ytdlp

router = APIRouter(
    prefix="/ytdlp",
    tags=["Tools"]
)

@router.get("/status", status_code=200)
def status() -> YTDLPStatus:
    return get_status()

@router.post("/update", status_code=200)
def update() -> YTDLPUpdateResult | dict[str, str]:
    try:
        result = update_ytdlp()
        return result
    except YTDLPUpdateAlreadyRunningError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )
    except YTDLPAlreadyUpToDateError as e:
        raise HTTPException(
            status_code=200,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )