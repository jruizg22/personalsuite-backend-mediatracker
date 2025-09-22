from typing import Callable, Generator, Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from media_tracker.models.yt import YTPlaylistVideoPublic, YTPlaylistVideoCreate, YTPlaylistVideoUpdate
from media_tracker.responses.youtube_responses import YTPlaylistVideoResponse, YTPlaylistVideoResponseItem
from media_tracker.services.youtube import yt_playlist_video_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/playlists_videos",
        tags=["YouTube Playlists Videos (association)"]
    )

    @router.get("/", response_model=YTPlaylistVideoResponse, status_code=200)
    def get_all_yt_playlists_videos(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
    ) -> YTPlaylistVideoResponse:
        """
        Retrieve a list of YouTube playlists videos items with optional pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).

        Returns:
            YTPlaylistVideoResponse: A list of YouTube playlists videos items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return yt_playlist_video_service.get_all(session, offset, limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube playlists videos: {e}"))

    @router.get("/{yt_playlists_videos_id}", response_model=YTPlaylistVideoResponseItem, status_code=200)
    def get_yt_playlists_videos_by_id(
            yt_playlists_videos_id: int,
            session: Session = Depends(get_session),
    ) -> YTPlaylistVideoResponseItem:
        """
        Retrieve a single YouTube playlists videos item by its ID.

        Args:
            yt_playlists_videos_id (int): The unique identifier of the YouTube playlists videos to retrieve.
            session (Session): Database session dependency.

        Returns:
            YTPlaylistVideoResponseItem: YTPlaylistVideo object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the YouTube playlists videos is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return yt_playlist_video_service.get_by_id(session, yt_playlists_videos_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube playlists videos with ID {yt_playlists_videos_id}: {e}"))

    @router.post("/", response_model=YTPlaylistVideoPublic, status_code=201)
    def create_yt_playlists_videos(new_yt_playlists_videos: YTPlaylistVideoCreate, session: Session = Depends(get_session)) -> YTPlaylistVideoPublic:
        """
        Create a new YouTube playlists videos entry in the database.

        Args:
            new_yt_playlists_videos (YTPlaylistVideoCreate): Data for the new YouTube playlists videos.
            session (Session): Database session dependency.

        Returns:
            YTPlaylistVideoPublic: Newly created YouTube playlists videos object.

        Raises:
            HTTPException: 500 if there is an error creating the YouTube playlists videos.
        """
        try:
            return yt_playlist_video_service.create(session, new_yt_playlists_videos)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating YouTube playlists videos: {e}"))

    @router.put("/{yt_playlists_videos_id}", response_model=YTPlaylistVideoPublic, status_code=200)
    def update_yt_playlists_videos(yt_playlists_videos_id: int, yt_playlists_videos_in: YTPlaylistVideoUpdate, session: Session = Depends(get_session)) -> YTPlaylistVideoPublic:
        """
        Update an existing YouTube playlists videos entry by its ID.

        Args:
            yt_playlists_videos_id (int): The ID of the YouTube playlists videos to update.
            yt_playlists_videos_in (YTPlaylistVideoUpdate): Data to update on the YouTube playlists videos.
            session (Session): Database session dependency.

        Returns:
            YTPlaylistVideoPublic: Updated YouTube playlists videos object.

        Raises:
            HTTPException: 404 if the YouTube playlists videos is not found.
            HTTPException: 500 if there is an error updating the YouTube playlists videos.
        """
        try:
            return yt_playlist_video_service.update(session, yt_playlists_videos_id, yt_playlists_videos_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating YouTube playlists videos with ID {yt_playlists_videos_id}: {e}"))

    @router.delete("/{yt_playlists_videos_id}", status_code=204)
    def delete_yt_playlists_videos(yt_playlists_videos_id: int, session: Session = Depends(get_session)) -> None:
        """
        Delete a YouTube playlists videos entry by its ID.

        Args:
            yt_playlists_videos_id (int): The ID of the YouTube playlists videos to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the YouTube playlists videos is not found.
            HTTPException: 500 if there is an error deleting the YouTube playlists videos.
        """
        try:
            yt_playlist_video_service.delete(session, yt_playlists_videos_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting YouTube playlists videos with ID {yt_playlists_videos_id}: {e}"))

    return router