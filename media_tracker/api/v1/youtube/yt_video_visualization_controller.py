from typing import Callable, Generator, Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from media_tracker.models.yt import YTVideoVisualizationPublic, YTVideoVisualizationCreate, YTVideoVisualizationUpdate
from media_tracker.responses.youtube_responses import YTVideoVisualizationResponse, YTVideoVisualizationResponseItem
from media_tracker.services.youtube import yt_video_visualization_service
from media_tracker.views.youtube_views import YTVideoVisualizationView


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/videos/visualizations",
        tags=["YouTube Video Visualizations"]
    )

    @router.get("/", response_model=YTVideoVisualizationResponse, status_code=200)
    def get_all_yt_video_visualizations(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: YTVideoVisualizationView = YTVideoVisualizationView.BASIC
    ) -> YTVideoVisualizationResponse:
        """
        Retrieve a list of YouTube video visualization items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (YTVideoVisualizationView): Determines which related data to include in the response
                              (basic, with video, etc.).

        Returns:
            YTVideoVisualizationResponse: A list of YouTube video visualization items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return yt_video_visualization_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube video visualizations: {e}"))

    @router.get("/{yt_video_visualization_id}", response_model=YTVideoVisualizationResponseItem, status_code=200)
    def get_yt_video_visualization_by_id(
            yt_video_visualization_id: int,
            session: Session = Depends(get_session),
            view: YTVideoVisualizationView = YTVideoVisualizationView.BASIC
    ) -> YTVideoVisualizationResponseItem:
        """
        Retrieve a single YouTube video visualization item by its ID.

        Args:
            yt_video_visualization_id (int): The unique identifier of the YouTube video visualization to retrieve.
            session (Session): Database session dependency.
            view (YTVideoVisualizationView, optional): Level of detail for the returned YouTube video visualization.
                Defaults to YTVideoVisualizationView.BASIC.

        Returns:
            YTVideoVisualizationResponseItem: YTVideoVisualization object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the YouTube video visualization is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return yt_video_visualization_service.get_by_id(session, yt_video_visualization_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube video visualization with ID {yt_video_visualization_id}: {e}"))

    @router.post("/", response_model=YTVideoVisualizationPublic, status_code=201)
    def create_yt_video_visualization(new_yt_video_visualization: YTVideoVisualizationCreate, session: Session = Depends(get_session)) -> YTVideoVisualizationPublic:
        """
        Create a new YouTube video visualization entry in the database.

        Args:
            new_yt_video_visualization (YTVideoVisualizationCreate): Data for the new YouTube video visualization.
            session (Session): Database session dependency.

        Returns:
            YTVideoVisualizationPublic: Newly created YouTube video visualization object.

        Raises:
            HTTPException: 500 if there is an error creating the YouTube video visualization.
        """
        try:
            return yt_video_visualization_service.create(session, new_yt_video_visualization)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating YouTube video visualization: {e}"))

    @router.put("/{yt_video_visualization_id}", response_model=YTVideoVisualizationPublic, status_code=200)
    def update_yt_video_visualization(yt_video_visualization_id: int, yt_video_visualization_in: YTVideoVisualizationUpdate, session: Session = Depends(get_session)) -> YTVideoVisualizationPublic:
        """
        Update an existing YouTube video visualization entry by its ID.

        Args:
            yt_video_visualization_id (int): The ID of the YouTube video visualization to update.
            yt_video_visualization_in (YTVideoVisualizationUpdate): Data to update on the YouTube video visualization.
            session (Session): Database session dependency.

        Returns:
            YTVideoVisualizationPublic: Updated YouTube video visualization object.

        Raises:
            HTTPException: 404 if the YouTube video visualization is not found.
            HTTPException: 500 if there is an error updating the YouTube video visualization.
        """
        try:
            return yt_video_visualization_service.update(session, yt_video_visualization_id, yt_video_visualization_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating YouTube video visualization with ID {yt_video_visualization_id}: {e}"))

    @router.delete("/{yt_video_visualization_id}", status_code=204)
    def delete_yt_video_visualization(yt_video_visualization_id: int, session: Session = Depends(get_session)) -> None:
        """
        Delete a YouTube video visualization entry by its ID.

        Args:
            yt_video_visualization_id (int): The ID of the YouTube video visualization to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the YouTube video visualization is not found.
            HTTPException: 500 if there is an error deleting the YouTube video visualization.
        """
        try:
            yt_video_visualization_service.delete(session, yt_video_visualization_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting YouTube video visualization with ID {yt_video_visualization_id}: {e}"))

    return router