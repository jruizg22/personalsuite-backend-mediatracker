from typing import Generator, Any, Callable

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session

from media_tracker.misc.responses import TVShowEpisodeTranslationResponse, TVShowEpisodeTranslationResponseItem
from media_tracker.misc.views import TVShowEpisodeTranslationView
from media_tracker.models.media import TVShowEpisodeTranslationPublic, TVShowEpisodeTranslationCreate, TVShowEpisodeTranslationUpdate
from media_tracker.services import tv_show_episode_translation_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:

    router: APIRouter = APIRouter(
        prefix="/media/translations",
        tags=["Media Translations"]
    )

    @router.get("/", response_model=TVShowEpisodeTranslationResponse, status_code=200)
    def get_all_tv_show_episode_translations(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: TVShowEpisodeTranslationView = TVShowEpisodeTranslationView.BASIC
    ) -> TVShowEpisodeTranslationResponse:
        """
        Retrieve a list of TV show episode translation items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (TVShowEpisodeTranslationView): Determines which related data to include in the response
                              (basic, with media, etc.).

        Returns:
            TVShowEpisodeTranslationResponse: A list of TV show episode translation items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return tv_show_episode_translation_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching TV show episode translation: {e}"))

    @router.get("/{tv_show_episode_translation_id}", response_model=TVShowEpisodeTranslationResponseItem, status_code=200)
    def get_tv_show_episode_translation_by_id(
            tv_show_episode_translation_id: int,
            language_code: str = None,
            session: Session = Depends(get_session),
            view: TVShowEpisodeTranslationView = TVShowEpisodeTranslationView.BASIC
    ) -> TVShowEpisodeTranslationResponseItem:
        """
        Retrieve a single TV show episode translation item by its ID.

        Args:
            tv_show_episode_translation_id (int): The unique identifier of the TV show episode translation to retrieve.
            language_code (str): The language code of the TV show episode translation to retrieve. If left None, all the translations with the same ID will be retrieved.
            session (Session): Database session dependency.
            view (TVShowEpisodeTranslationView): Level of detail for the returned TV show episode translation.
                Defaults to TVShowEpisodeTranslationView.BASIC.

        Returns:
            TVShowEpisodeTranslationResponseItem: TVShowEpisodeTranslation object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the TV show episode translation is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return tv_show_episode_translation_service.get_by_id(session, tv_show_episode_translation_id, language_code, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            if not language_code:
                raise HTTPException(status_code=500, detail=(f"Error fetching TV show episode translation with ID {tv_show_episode_translation_id}: {e}"))
            else:
                raise HTTPException(status_code=500, detail=(f"Error fetching TV show episode translation with ID {tv_show_episode_translation_id} and language code {language_code}: {e}"))

    @router.post("/", response_model=TVShowEpisodeTranslationPublic, status_code=201)
    def create_tv_show_episode_translation(new_tv_show_episode_translation: TVShowEpisodeTranslationCreate, session: Session = Depends(get_session)) -> TVShowEpisodeTranslationPublic:
        """
        Create a new TV show episode translation entry in the database.

        Args:
            new_tv_show_episode_translation (TVShowEpisodeTranslationCreate): Data for the new TV show episode translation.
            session (Session): Database session dependency.

        Returns:
            TVShowEpisodeTranslationPublic: Newly created TV show episode translation object.

        Raises:
            HTTPException: 500 if there is an error creating the TV show episode translation.
        """
        try:
            return tv_show_episode_translation_service.create(session, new_tv_show_episode_translation)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating TV show episode translation: {e}"))

    @router.put("/{tv_show_episode_translation_id}", response_model=TVShowEpisodeTranslationPublic, status_code=200)
    def update_tv_show_episode_translation(tv_show_episode_translation_id: int, language_code: str, tv_show_episode_translation_in: TVShowEpisodeTranslationUpdate, session: Session = Depends(get_session)) -> TVShowEpisodeTranslationPublic:
        """
        Update an existing media entry by its ID.

        Args:
            tv_show_episode_translation_id (int): The ID of the TV show episode translation to update.
            language_code (str): The language code of the TV show episode translation to update.
            tv_show_episode_translation_in (TVShowEpisodeTranslationUpdate): Data to update on the TV show episode translation.
            session (Session): Database session dependency.

        Returns:
            TVShowEpisodeTranslationPublic: Updated TV show episode translation object.

        Raises:
            HTTPException: 404 if the TV show episode translation is not found.
            HTTPException: 500 if there is an error updating the TV show episode translation.
        """
        try:
            return tv_show_episode_translation_service.update(session, tv_show_episode_translation_id, language_code, tv_show_episode_translation_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating TV show episode translation with ID {tv_show_episode_translation_id} and language code {language_code}: {e}"))

    @router.delete("/{tv_show_episode_translation_id}", status_code=204)
    def delete_tv_show_episode_translation(tv_show_episode_translation_id: int, language_code: str, session: Session = Depends(get_session)) -> None:
        """
        Delete a TV show episode translation entry by its ID.

        Args:
            tv_show_episode_translation_id (int): The ID of the TV show episode translation to delete.
            language_code (str): The language code of the TV show episode translation to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the TV show episode translation is not found.
            HTTPException: 500 if there is an error deleting the TV show episode translation.
        """
        try:
            tv_show_episode_translation_service.delete(session, tv_show_episode_translation_id, language_code)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting TV show episode translation with ID {tv_show_episode_translation_id} and language code {language_code}: {e}"))

    return router