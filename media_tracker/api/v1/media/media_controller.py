from typing import Generator, Any, Callable

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session

from media_tracker.responses.media_responses import MediaResponse, MediaResponseItem
from media_tracker.views.media_views import MediaView
from media_tracker.models.media import MediaType, MediaPublic, MediaCreate, MediaUpdate
from media_tracker.services.media import media_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
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
        """
        Retrieve a single media item by its ID.

        Args:
            media_id (int): The unique identifier of the media to retrieve.
            session (Session): Database session dependency.
            view (MediaView, optional): Level of detail for the returned media.
                Defaults to MediaView.BASIC.

        Returns:
            MediaResponseItem: Media object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the media is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return media_service.get_by_id(session, media_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching media with ID {media_id}: {e}"))

    @router.post("/", response_model=MediaPublic, status_code=201)
    def create_media(new_media: MediaCreate, session: Session = Depends(get_session)) -> MediaPublic:
        """
        Create a new media entry in the database.

        Args:
            new_media (MediaCreate): Data for the new media.
            session (Session): Database session dependency.

        Returns:
            MediaPublic: Newly created media object.

        Raises:
            HTTPException: 500 if there is an error creating the media.
        """
        try:
            return media_service.create(session, new_media)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating media: {e}"))

    @router.put("/{media_id}", response_model=MediaPublic, status_code=200)
    def update_media(media_id: int, media_in: MediaUpdate, session: Session = Depends(get_session)) -> MediaPublic:
        """
        Update an existing media entry by its ID.

        Args:
            media_id (int): The ID of the media to update.
            media_in (MediaUpdate): Data to update on the media.
            session (Session): Database session dependency.

        Returns:
            MediaPublic: Updated media object.

        Raises:
            HTTPException: 404 if the media is not found.
            HTTPException: 500 if there is an error updating the media.
        """
        try:
            return media_service.update(session, media_id, media_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating media with ID {media_id}: {e}"))

    @router.delete("/{media_id}", status_code=204)
    def delete_media(media_id: int, session: Session = Depends(get_session)) -> None:
        """
        Delete a media entry by its ID.

        Args:
            media_id (int): The ID of the media to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the media is not found.
            HTTPException: 500 if there is an error deleting the media.
        """
        try:
            media_service.delete(session, media_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting media with ID {media_id}: {e}"))

    return router