from typing import Generator, Any, Callable

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session

from media_tracker.misc.responses import TVShowEpisodeVisualizationResponse, TVShowEpisodeVisualizationResponseItem
from media_tracker.misc.views import TVShowEpisodeVisualizationView
from media_tracker.models.media import TVShowEpisodeVisualizationPublic, TVShowEpisodeVisualizationCreate, TVShowEpisodeVisualizationUpdate
from media_tracker.services import tv_show_episode_visualization_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:

    router: APIRouter = APIRouter(
        prefix="/media/tv_show_episodes/visualizations",
        tags=["TV Show Episodes Visualizations"]
    )

    @router.get("/", response_model=TVShowEpisodeVisualizationResponse, status_code=200)
    def get_all_tv_show_episode_visualizations(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: TVShowEpisodeVisualizationView = TVShowEpisodeVisualizationView.BASIC
    ) -> TVShowEpisodeVisualizationResponse:
        """
        Retrieve a list of TV show episode visualization items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (TVShowEpisodeVisualizationView): Determines which related data to include in the response
                              (basic, with TV show episode, etc.).

        Returns:
            TVShowEpisodeVisualizationResponse: A list of TV show episode visualization items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return tv_show_episode_visualization_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching TV show episode visualization: {e}"))

    @router.get("/{tv_show_episode_visualization_id}", response_model=TVShowEpisodeVisualizationResponseItem, status_code=200)
    def get_tv_show_episode_visualizations_by_id(
            tv_show_episode_visualization_id: int,
            session: Session = Depends(get_session),
            view: TVShowEpisodeVisualizationView = TVShowEpisodeVisualizationView.BASIC
    ) -> TVShowEpisodeVisualizationResponseItem:
        """
        Retrieve a single TV show episode visualization item by its ID.

        Args:
            tv_show_episode_visualization_id (int): The unique identifier of the TV show episode visualization to retrieve.
            session (Session): Database session dependency.
            view (TVShowEpisodeVisualizationView): Level of detail for the returned TV show episode visualization.
                Defaults to TVShowEpisodeVisualizationView.BASIC.

        Returns:
            TVShowEpisodeVisualizationResponseItem: TVShowEpisodeVisualization object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the TV show episode visualization is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return tv_show_episode_visualization_service.get_by_id(session, tv_show_episode_visualization_id, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching TV show episode visualization with ID {tv_show_episode_visualization_id}: {e}"))

    @router.post("/", response_model=TVShowEpisodeVisualizationPublic, status_code=201)
    def create_tv_show_episode_visualization(new_tv_show_episode_visualization: TVShowEpisodeVisualizationCreate, session: Session = Depends(get_session)) -> TVShowEpisodeVisualizationPublic:
        """
        Create a new TV show episode visualization entry in the database.

        Args:
            new_tv_show_episode_visualization (TVShowEpisodeVisualizationCreate): Data for the new TV show episode visualization.
            session (Session): Database session dependency.

        Returns:
            TVShowEpisodeVisualizationPublic: Newly created TV show episode visualization object.

        Raises:
            HTTPException: 500 if there is an error creating the TV show episode visualization.
        """
        try:
            return tv_show_episode_visualization_service.create(session, new_tv_show_episode_visualization)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating TV show episode visualization: {e}"))

    @router.put("/{tv_show_episode_visualization_id}", response_model=TVShowEpisodeVisualizationPublic, status_code=200)
    def update_tv_show_episode_visualization(tv_show_episode_visualization_id: int, tv_show_episode_visualization_in: TVShowEpisodeVisualizationUpdate, session: Session = Depends(get_session)) -> TVShowEpisodeVisualizationPublic:
        """
        Update an existing media entry by its ID.

        Args:
            tv_show_episode_visualization_id (int): The ID of the TV show episode visualization to update.
            tv_show_episode_visualization_in (TVShowEpisodeVisualizationUpdate): Data to update on the TV show episode visualization.
            session (Session): Database session dependency.

        Returns:
            TVShowEpisodeVisualizationPublic: Updated TV show episode visualization object.

        Raises:
            HTTPException: 404 if the TV show episode visualization is not found.
            HTTPException: 500 if there is an error updating the TV show episode visualization.
        """
        try:
            return tv_show_episode_visualization_service.update(session, tv_show_episode_visualization_id, tv_show_episode_visualization_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating TV show episode visualization with ID {tv_show_episode_visualization_id}: {e}"))

    @router.delete("/{tv_show_episode_visualization_id}", status_code=204)
    def delete_tv_show_episode_visualization(tv_show_episode_visualization_id: int, session: Session = Depends(get_session)) -> None:
        """
        Delete a TV show episode visualization entry by its ID.

        Args:
            tv_show_episode_visualization_id (int): The ID of the TV show episode visualization to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the TV show episode visualization is not found.
            HTTPException: 500 if there is an error deleting the TV show episode visualization.
        """
        try:
            tv_show_episode_visualization_service.delete(session, tv_show_episode_visualization_id)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting TV show episode visualization with ID {tv_show_episode_visualization_id}: {e}"))

    return router