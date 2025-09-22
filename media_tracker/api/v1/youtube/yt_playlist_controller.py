from typing import Callable, Generator, Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from media_tracker.models.yt import YTPlaylistPublic, YTPlaylistCreate, YTPlaylistUpdate
from media_tracker.responses.youtube_responses import YTPlaylistResponse, YTPlaylistResponseItem
from media_tracker.services.youtube import yt_playlist_service
from media_tracker.views.youtube_views import YTPlaylistView


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/playlists",
        tags=["YouTube Playlists"]
    )

    @router.get("/", response_model=YTPlaylistResponse, status_code=200)
    def get_all_yt_playlists(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: YTPlaylistView = YTPlaylistView.BASIC
    ) -> YTPlaylistResponse:
        """
        Retrieve a list of YouTube playlist items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (YTPlaylistView): Determines which related data to include in the response
                              (basic, with videos, channel, full, etc.).

        Returns:
            YTPlaylistResponse: A list of YouTube playlist items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return yt_playlist_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube playlists: {e}"))

    @router.get("/{yt_playlist_id}", response_model=YTPlaylistResponseItem, status_code=200)
    def get_yt_playlist_by_id(
            yt_playlist_id: str,
            session: Session = Depends(get_session),
            view: YTPlaylistView = YTPlaylistView.BASIC
    ) -> YTPlaylistResponseItem:
        """
        Retrieve a single YouTube playlist item by its ID.

        Args:
            yt_playlist_id (str): The unique identifier of the YouTube playlist to retrieve.
            session (Session): Database session dependency.
            view (YTPlaylistView, optional): Level of detail for the returned YouTube playlist.
                Defaults to YTPlaylistView.BASIC.

        Returns:
            YTPlaylistResponseItem: YTPlaylist object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the YouTube playlist is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return yt_playlist_service.get_by_id(session, yt_playlist_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube playlist with ID {yt_playlist_id}: {e}"))

    @router.post("/", response_model=YTPlaylistPublic, status_code=201)
    def create_yt_playlist(new_yt_playlist: YTPlaylistCreate, session: Session = Depends(get_session)) -> YTPlaylistPublic:
        """
        Create a new YouTube playlist entry in the database.

        Args:
            new_yt_playlist (YTPlaylistCreate): Data for the new YouTube playlist.
            session (Session): Database session dependency.

        Returns:
            YTPlaylistPublic: Newly created YouTube playlist object.

        Raises:
            HTTPException: 500 if there is an error creating the YouTube playlist.
        """
        try:
            return yt_playlist_service.create(session, new_yt_playlist)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating YouTube playlist: {e}"))

    @router.put("/{yt_playlist_id}", response_model=YTPlaylistPublic, status_code=200)
    def update_yt_playlist(yt_playlist_id: str, yt_playlist_in: YTPlaylistUpdate, session: Session = Depends(get_session)) -> YTPlaylistPublic:
        """
        Update an existing YouTube playlist entry by its ID.

        Args:
            yt_playlist_id (str): The ID of the YouTube playlist to update.
            yt_playlist_in (YTPlaylistUpdate): Data to update on the YouTube playlist.
            session (Session): Database session dependency.

        Returns:
            YTPlaylistPublic: Updated YouTube playlist object.

        Raises:
            HTTPException: 404 if the YouTube playlist is not found.
            HTTPException: 500 if there is an error updating the YouTube playlist.
        """
        try:
            return yt_playlist_service.update(session, yt_playlist_id, yt_playlist_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating YouTube playlist with ID {yt_playlist_id}: {e}"))

    @router.delete("/{yt_playlist_id}", status_code=204)
    def delete_yt_playlist(yt_playlist_id: str, session: Session = Depends(get_session)) -> None:
        """
        Delete a YouTube playlist entry by its ID.

        Args:
            yt_playlist_id (str): The ID of the YouTube playlist to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the YouTube playlist is not found.
            HTTPException: 500 if there is an error deleting the YouTube playlist.
        """
        try:
            yt_playlist_service.delete(session, yt_playlist_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting YouTube playlist with ID {yt_playlist_id}: {e}"))

    return router