from typing import Callable, Generator, Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from media_tracker.models.yt import YTVideoPublic, YTVideoCreate, YTVideoUpdate
from media_tracker.responses.youtube_responses import YTVideoResponse, YTVideoResponseItem
from media_tracker.services.youtube import yt_video_service
from media_tracker.views.youtube_views import YTVideoView


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/videos",
        tags=["YouTube Videos"]
    )

    @router.get("/", response_model=YTVideoResponse, status_code=200)
    def get_all_yt_videos(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: YTVideoView = YTVideoView.BASIC
    ) -> YTVideoResponse:
        """
        Retrieve a list of YouTube video items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (YTVideoView): Determines which related data to include in the response
                              (basic, with visualizations, playlists, channels, etc.).

        Returns:
            YTVideoResponse: A list of YouTube video items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return yt_video_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube videos: {e}"))

    @router.get("/channel/{channel_id}", response_model=list[YTVideoPublic], status_code=200)
    def get_all_yt_videos_by_channel_id(
            channel_id: str,
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1)
    ) -> list[YTVideoPublic]:
        """
        Retrieve a list of YouTube videos belonging to a specific channel.

        Args:
            channel_id (str): The unique identifier of the YouTube channel.
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).

        Returns:
            list[YTVideoPublic]: A list of YouTube video objects from the specified channel.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return yt_video_service.get_all_by_channel_id(channel_id, session, offset, limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube videos by channel id: {e}"))

    @router.get("/{yt_video_id}", response_model=YTVideoResponseItem, status_code=200)
    def get_yt_video_by_id(
            yt_video_id: str,
            session: Session = Depends(get_session),
            view: YTVideoView = YTVideoView.BASIC
    ) -> YTVideoResponseItem:
        """
        Retrieve a single YouTube video item by its ID.

        Args:
            yt_video_id (str): The unique identifier of the YouTube video to retrieve.
            session (Session): Database session dependency.
            view (YTVideoView, optional): Level of detail for the returned YouTube video.
                Defaults to YTVideoView.BASIC.

        Returns:
            YTVideoResponseItem: YTVideo object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the YouTube video is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return yt_video_service.get_by_id(session, yt_video_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube video with ID {yt_video_id}: {e}"))

    @router.post("/", response_model=YTVideoPublic, status_code=201)
    def create_yt_video(new_yt_video: YTVideoCreate, session: Session = Depends(get_session)) -> YTVideoPublic:
        """
        Create a new YouTube video entry in the database.

        Args:
            new_yt_video (YTVideoCreate): Data for the new YouTube video.
            session (Session): Database session dependency.

        Returns:
            YTVideoPublic: Newly created YouTube video object.

        Raises:
            HTTPException: 500 if there is an error creating the YouTube video.
        """
        try:
            return yt_video_service.create(session, new_yt_video)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating YouTube video: {e}"))

    @router.put("/{yt_video_id}", response_model=YTVideoPublic, status_code=200)
    def update_yt_video(yt_video_id: str, yt_video_in: YTVideoUpdate, session: Session = Depends(get_session)) -> YTVideoPublic:
        """
        Update an existing YouTube video entry by its ID.

        Args:
            yt_video_id (str): The ID of the YouTube video to update.
            yt_video_in (YTVideoUpdate): Data to update on the YouTube video.
            session (Session): Database session dependency.

        Returns:
            YTVideoPublic: Updated YouTube video object.

        Raises:
            HTTPException: 404 if the YouTube video is not found.
            HTTPException: 500 if there is an error updating the YouTube video.
        """
        try:
            return yt_video_service.update(session, yt_video_id, yt_video_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating YouTube video with ID {yt_video_id}: {e}"))

    @router.delete("/{yt_video_id}", status_code=204)
    def delete_yt_video(yt_video_id: str, session: Session = Depends(get_session)) -> None:
        """
        Delete a YouTube video entry by its ID.

        Args:
            yt_video_id (str): The ID of the YouTube video to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the YouTube video is not found.
            HTTPException: 500 if there is an error deleting the YouTube video.
        """
        try:
            yt_video_service.delete(session, yt_video_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting YouTube video with ID {yt_video_id}: {e}"))

    return router