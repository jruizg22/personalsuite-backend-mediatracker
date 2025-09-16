from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from media_tracker.models.media import MediaPublic
from media_tracker.services import media_service

router = APIRouter(
    prefix="/media",
    tags=["media"],
)

@router.get("/", response_model=list[MediaPublic])
def get_all(session: Session = Depends()) -> list[MediaPublic]:
    try:
        return media_service.get_all(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=(f"Error fetching media: {e}"))