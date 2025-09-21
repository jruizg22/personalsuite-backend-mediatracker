from typing import Generator, Any, Callable

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session

from media_tracker.responses.media_responses import TVShowEpisodeResponse, TVShowEpisodeResponseItem
from media_tracker.views.media_views import TVShowEpisodeView
from media_tracker.models.media import TVShowEpisodePublic, TVShowEpisodeCreate, TVShowEpisodeUpdate
from media_tracker.services import tv_show_episode_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:

    router: APIRouter = APIRouter(
        prefix="/tv_show_episodes",
        tags=["TV Show Episodes"]
    )

    @router.get("/", response_model=TVShowEpisodeResponse, status_code=200)
    def get_all_tv_show_episodes(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: TVShowEpisodeView = TVShowEpisodeView.BASIC
    ) -> TVShowEpisodeResponse:
        """
        Retrieve a list of TV show episode items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (TVShowEpisodeView): Determines which related data to include in the response
                              (basic, with media, etc.).

        Returns:
            TVShowEpisodeResponse: A list of TV show episode items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return tv_show_episode_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching TV show episode: {e}"))

    @router.get("/{tv_show_episode_id}", response_model=TVShowEpisodeResponseItem, status_code=200)
    def get_tv_episode_by_id(
            tv_show_episode_id: int,
            session: Session = Depends(get_session),
            view: TVShowEpisodeView = TVShowEpisodeView.BASIC
    ) -> TVShowEpisodeResponseItem:
        """
        Retrieve a single TV show episode item by its ID.

        Args:
            tv_show_episode_id (int): The unique identifier of the TV show episode to retrieve.
            session (Session): Database session dependency.
            view (TVShowEpisodeView): Level of detail for the returned TV show episode.
                Defaults to TVShowEpisodeView.BASIC.

        Returns:
            TVShowEpisodeResponseItem: TVShowEpisode object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the TV show episode is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return tv_show_episode_service.get_by_id(session, tv_show_episode_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching TV show episode with ID {tv_show_episode_id}: {e}"))

    @router.post("/", response_model=TVShowEpisodePublic, status_code=201)
    def create_media(new_tv_show_episode: TVShowEpisodeCreate, session: Session = Depends(get_session)) -> TVShowEpisodePublic:
        """
        Create a new TV show episode entry in the database.

        Args:
            new_tv_show_episode (TVShowEpisodeCreate): Data for the new TV show episode.
            session (Session): Database session dependency.

        Returns:
            TVShowEpisodePublic: Newly created TV show episode object.

        Raises:
            HTTPException: 500 if there is an error creating the TV show episode.
        """
        try:
            return tv_show_episode_service.create(session, new_tv_show_episode)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating TV show episode: {e}"))

    @router.put("/{tv_show_episode_id}", response_model=TVShowEpisodePublic, status_code=200)
    def update_media(tv_show_episode_id: int, tv_show_episode_in: TVShowEpisodeUpdate, session: Session = Depends(get_session)) -> TVShowEpisodePublic:
        """
        Update an existing media entry by its ID.

        Args:
            tv_show_episode_id (int): The ID of the TV show episode to update.
            tv_show_episode_in (TVShowEpisodeUpdate): Data to update on the TV show episode.
            session (Session): Database session dependency.

        Returns:
            TVShowEpisodePublic: Updated TV show episode object.

        Raises:
            HTTPException: 404 if the TV show episode is not found.
            HTTPException: 500 if there is an error updating the TV show episode.
        """
        try:
            return tv_show_episode_service.update(session, tv_show_episode_id, tv_show_episode_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating TV show episode with ID {tv_show_episode_id}: {e}"))

    @router.delete("/{tv_show_episode_id}", status_code=204)
    def delete_media(tv_show_episode_id: int, session: Session = Depends(get_session)) -> None:
        """
        Delete a TV show episode entry by its ID.

        Args:
            tv_show_episode_id (int): The ID of the TV show episode to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the TV show episode is not found.
            HTTPException: 500 if there is an error deleting the TV show episode.
        """
        try:
            tv_show_episode_service.delete(session, tv_show_episode_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting TV show episode with ID {tv_show_episode_id}: {e}"))

    return router