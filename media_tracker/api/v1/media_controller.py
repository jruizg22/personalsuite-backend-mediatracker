from typing import Generator, Any, Callable

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session

from media_tracker.models.media import MediaResponse, MediaResponseItem, MediaType, MediaView, MediaPublic, MediaCreate, MediaUpdate
from media_tracker.services import media_service

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError # type: ignore


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/media",
        tags=["Media"]
    )

    @router.get("/", response_model=MediaResponse, status_code=200)
    def get_all_media(
            session: Session = Depends(get_session),
            media_type: MediaType | None = None,
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: MediaView = MediaView.BASIC
) -> MediaResponse:
        """
        Retrieve a list of media items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            media_type (MediaType | None): Optional filter by media type (movie, TV show, etc.).
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (MediaView): Determines which related data to include in the response
                              (basic, with translations, visualizations, full, etc.).

        Returns:
            MediaResponse: A list of media items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return media_service.get_all(session, media_type, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching media: {e}"))

    @router.get("/{media_id}", response_model=MediaResponseItem, status_code=200)
    def get_media_by_id(
            media_id: int,
            session: Session = Depends(get_session),
            view: MediaView = MediaView.BASIC
    ) -> MediaResponseItem:
        try:
            return media_service.get_by_id(session, media_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching media with ID {media_id}: {e}"))

    @router.post("/", response_model=MediaPublic, status_code=201)
    def create_media(new_media: MediaCreate, session: Session = Depends(get_session)) -> MediaPublic:
        try:
            return media_service.create(session, new_media)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating media: {e}"))

    @router.put("/{media_id}", response_model=MediaPublic, status_code=200)
    def update_media(media_id: int, media_in: MediaUpdate, session: Session = Depends(get_session)) -> MediaPublic:
        try:
            return media_service.update(session, media_id, media_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating media with ID {media_id}: {e}"))

    @router.delete("/{media_id}", status_code=204)
    def delete_media(media_id: int, session: Session = Depends(get_session)) -> None:
        try:
            media_service.delete(session, media_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting media with ID {media_id}: {e}"))

    return router