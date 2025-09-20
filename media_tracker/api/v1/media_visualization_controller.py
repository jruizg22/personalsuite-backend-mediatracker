from typing import Generator, Any, Callable

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session

from media_tracker.misc.responses import MediaVisualizationResponse, MediaVisualizationResponseItem
from media_tracker.misc.views import MediaVisualizationView
from media_tracker.models.media import MediaVisualizationPublic, MediaVisualizationCreate, MediaVisualizationUpdate
from media_tracker.services import media_visualization_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:

    router: APIRouter = APIRouter(
        prefix="/media/visualizations",
        tags=["Media Visualizations"]
    )

    @router.get("/", response_model=MediaVisualizationResponse, status_code=200)
    def get_all_media_visualizations(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: MediaVisualizationView = MediaVisualizationView.BASIC
    ) -> MediaVisualizationResponse:
        """
        Retrieve a list of media visualization items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (MediaVisualizationView): Determines which related data to include in the response
                              (basic, with media, etc.).

        Returns:
            MediaVisualizationResponse: A list of media visualization items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return media_visualization_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching media visualization: {e}"))

    @router.get("/{media_visualization_id}", response_model=MediaVisualizationResponseItem, status_code=200)
    def get_media_by_id(
            media_visualization_id: int,
            session: Session = Depends(get_session),
            view: MediaVisualizationView = MediaVisualizationView.BASIC
    ) -> MediaVisualizationResponseItem:
        """
        Retrieve a single media visualization item by its ID.

        Args:
            media_visualization_id (int): The unique identifier of the media visualization to retrieve.
            session (Session): Database session dependency.
            view (MediaVisualizationView): Level of detail for the returned media.
                Defaults to MediaVisualizationView.BASIC.

        Returns:
            MediaVisualizationResponseItem: MediaVisualization object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the media visualization is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return media_visualization_service.get_by_id(session, media_visualization_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching media visualization with ID {media_visualization_id}: {e}"))

    @router.post("/", response_model=MediaVisualizationPublic, status_code=201)
    def create_media(new_media_visualization: MediaVisualizationCreate, session: Session = Depends(get_session)) -> MediaVisualizationPublic:
        """
        Create a new media visualization entry in the database.

        Args:
            new_media_visualization (MediaVisualizationCreate): Data for the new media visualization.
            session (Session): Database session dependency.

        Returns:
            MediaVisualizationPublic: Newly created media visualization object.

        Raises:
            HTTPException: 500 if there is an error creating the media.
        """
        try:
            return media_visualization_service.create(session, new_media_visualization)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating media: {e}"))

    @router.put("/{media_visualization_id}", response_model=MediaVisualizationPublic, status_code=200)
    def update_media(media_visualization_id: int, media_visualization_in: MediaVisualizationUpdate, session: Session = Depends(get_session)) -> MediaVisualizationPublic:
        """
        Update an existing media entry by its ID.

        Args:
            media_visualization_id (int): The ID of the media visualization to update.
            media_visualization_in (MediaVisualizationUpdate): Data to update on the media visualization.
            session (Session): Database session dependency.

        Returns:
            MediaVisualizationPublic: Updated media visualization object.

        Raises:
            HTTPException: 404 if the media visualization is not found.
            HTTPException: 500 if there is an error updating the media.
        """
        try:
            return media_visualization_service.update(session, media_visualization_id, media_visualization_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating media visualization with ID {media_visualization_id}: {e}"))

    @router.delete("/{media_visualization_id}", status_code=204)
    def delete_media(media_visualization_id: int, session: Session = Depends(get_session)) -> None:
        """
        Delete a media visualization entry by its ID.

        Args:
            media_visualization_id (int): The ID of the media visualization to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the media visualization is not found.
            HTTPException: 500 if there is an error deleting the media.
        """
        try:
            media_visualization_service.delete(session, media_visualization_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting media with ID {media_visualization_id}: {e}"))

    return router