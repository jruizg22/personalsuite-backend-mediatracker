from typing import Callable, Generator, Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from media_tracker.models.yt import YTChannelPublic, YTChannelCreate, YTChannelUpdate
from media_tracker.responses.youtube_responses import YTChannelResponse, YTChannelResponseItem
from media_tracker.services.youtube import yt_channel_service
from media_tracker.views.youtube_views import YTChannelView


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:
    router: APIRouter = APIRouter(
        prefix="/channels",
        tags=["YouTube Channels"]
    )

    @router.get("/", response_model=YTChannelResponse, status_code=200)
    def get_all_yt_channels(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: YTChannelView = YTChannelView.BASIC
    ) -> YTChannelResponse:
        """
        Retrieve a list of YouTube channel items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (YTChannelView): Determines which related data to include in the response
                              (basic, with videos, playlists, full, etc.).

        Returns:
            YTChannelResponse: A list of YouTube channel items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return yt_channel_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube channels: {e}"))

    @router.get("/{yt_channel_id}", response_model=YTChannelResponseItem, status_code=200)
    def get_yt_channel_by_id(
            yt_channel_id: int,
            session: Session = Depends(get_session),
            view: YTChannelView = YTChannelView.BASIC
    ) -> YTChannelResponseItem:
        """
        Retrieve a single YouTube channel item by its ID.

        Args:
            yt_channel_id (int): The unique identifier of the YouTube channel to retrieve.
            session (Session): Database session dependency.
            view (YTChannelView, optional): Level of detail for the returned YouTube channel.
                Defaults to YTChannelView.BASIC.

        Returns:
            YTChannelResponseItem: YTChannel object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the YouTube channel is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return yt_channel_service.get_by_id(session, yt_channel_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching YouTube channel with ID {yt_channel_id}: {e}"))

    @router.post("/", response_model=YTChannelPublic, status_code=201)
    def create_yt_channel(new_yt_channel: YTChannelCreate, session: Session = Depends(get_session)) -> YTChannelPublic:
        """
        Create a new YouTube channel entry in the database.

        Args:
            new_yt_channel (YTChannelCreate): Data for the new YouTube channel.
            session (Session): Database session dependency.

        Returns:
            YTChannelPublic: Newly created YouTube channel object.

        Raises:
            HTTPException: 500 if there is an error creating the YouTube channel.
        """
        try:
            return yt_channel_service.create(session, new_yt_channel)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating YouTube channel: {e}"))

    @router.put("/{yt_channel_id}", response_model=YTChannelPublic, status_code=200)
    def update_yt_channel(yt_channel_id: int, yt_channel_in: YTChannelUpdate, session: Session = Depends(get_session)) -> YTChannelPublic:
        """
        Update an existing YouTube channel entry by its ID.

        Args:
            yt_channel_id (int): The ID of the YouTube channel to update.
            yt_channel_in (YTChannelUpdate): Data to update on the YouTube channel.
            session (Session): Database session dependency.

        Returns:
            YTChannelPublic: Updated YouTube channel object.

        Raises:
            HTTPException: 404 if the YouTube channel is not found.
            HTTPException: 500 if there is an error updating the YouTube channel.
        """
        try:
            return yt_channel_service.update(session, yt_channel_id, yt_channel_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating YouTube channel with ID {yt_channel_id}: {e}"))

    @router.delete("/{yt_channel_id}", status_code=204)
    def delete_yt_channel(yt_channel_id: int, session: Session = Depends(get_session)) -> None:
        """
        Delete a YouTube channel entry by its ID.

        Args:
            yt_channel_id (int): The ID of the YouTube channel to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the YouTube channel is not found.
            HTTPException: 500 if there is an error deleting the YouTube channel.
        """
        try:
            yt_channel_service.delete(session, yt_channel_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting YouTube channel with ID {yt_channel_id}: {e}"))

    return router