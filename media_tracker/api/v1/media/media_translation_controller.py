from typing import Generator, Any, Callable

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session

from media_tracker.responses.media_responses import MediaTranslationResponse, MediaTranslationResponseItem
from media_tracker.views.media_views import MediaTranslationView
from media_tracker.models.media import MediaTranslationPublic, MediaTranslationCreate, MediaTranslationUpdate
from media_tracker.services.media import media_translation_service


def get_router(get_session: Callable[[], Generator[Session, Any, None]]) -> APIRouter:

    router: APIRouter = APIRouter(
        prefix="/translations",
        tags=["Media Translations"]
    )

    @router.get("/", response_model=MediaTranslationResponse, status_code=200)
    def get_all_media_translations(
            session: Session = Depends(get_session),
            offset: int = Query(0, ge=0),
            limit: int = Query(100, ge=1),
            view: MediaTranslationView = MediaTranslationView.BASIC
    ) -> MediaTranslationResponse:
        """
        Retrieve a list of media translation items with optional filtering and pagination.

        Args:
            session (Session): Database session dependency.
            offset (int): Number of items to skip for pagination (default 0).
            limit (int): Maximum number of items to return (default 100).
            view (MediaTranslationView): Determines which related data to include in the response
                              (basic, with media, etc.).

        Returns:
            MediaTranslationResponse: A list of media translation items formatted according to the requested view.

        Raises:
            HTTPException: 500 if an unexpected error occurs during retrieval.
        """
        try:
            return media_translation_service.get_all(session, offset, limit, view)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error fetching media translation: {e}"))

    @router.get("/{media_translation_id}", response_model=MediaTranslationResponseItem, status_code=200)
    def get_media_translation_by_id(
            media_translation_id: int,
            language_code: str = None,
            session: Session = Depends(get_session),
            view: MediaTranslationView = MediaTranslationView.BASIC
    ) -> MediaTranslationResponseItem:
        """
        Retrieve a single media translation item by its ID.

        Args:
            media_translation_id (int): The unique identifier of the media translation to retrieve.
            language_code (str): The language code of the media translation to retrieve. If left None, all the translations with the same ID will be retrieved.
            session (Session): Database session dependency.
            view (MediaTranslationView): Level of detail for the returned media translation.
                Defaults to MediaTranslationView.BASIC.

        Returns:
            MediaTranslationResponseItem: MediaTranslation object with fields based on the requested view.

        Raises:
            HTTPException: 404 if the media translation is not found.
            HTTPException: 500 for unexpected errors during retrieval.
        """
        try:
            return media_translation_service.get_by_id(session, media_translation_id, language_code, view)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            if not language_code:
                raise HTTPException(status_code=500, detail=(f"Error fetching media translation with ID {media_translation_id}: {e}"))
            else:
                raise HTTPException(status_code=500, detail=(f"Error fetching media translation with ID {media_translation_id} and language code {language_code}: {e}"))

    @router.post("/", response_model=MediaTranslationPublic, status_code=201)
    def create_media_translation(new_media_translation: MediaTranslationCreate, session: Session = Depends(get_session)) -> MediaTranslationPublic:
        """
        Create a new media translation entry in the database.

        Args:
            new_media_translation (MediaTranslationCreate): Data for the new media translation.
            session (Session): Database session dependency.

        Returns:
            MediaTranslationPublic: Newly created media translation object.

        Raises:
            HTTPException: 500 if there is an error creating the media translation.
        """
        try:
            return media_translation_service.create(session, new_media_translation)
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error creating media translation: {e}"))

    @router.put("/{media_translation_id}", response_model=MediaTranslationPublic, status_code=200)
    def update_media_translation(media_translation_id: int, language_code: str, media_translation_in: MediaTranslationUpdate, session: Session = Depends(get_session)) -> MediaTranslationPublic:
        """
        Update an existing media entry by its ID.

        Args:
            media_translation_id (int): The ID of the media translation to update.
            language_code (str): The language code of the media translation to update.
            media_translation_in (MediaTranslationUpdate): Data to update on the media translation.
            session (Session): Database session dependency.

        Returns:
            MediaTranslationPublic: Updated media translation object.

        Raises:
            HTTPException: 404 if the media translation is not found.
            HTTPException: 500 if there is an error updating the media translation.
        """
        try:
            return media_translation_service.update(session, media_translation_id, language_code, media_translation_in)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error updating media translation with ID {media_translation_id} and language code {language_code}: {e}"))

    @router.delete("/{media_translation_id}", status_code=204)
    def delete_media_translation(media_translation_id: int, language_code: str, session: Session = Depends(get_session)) -> None:
        """
        Delete a media translation entry by its ID.

        Args:
            media_translation_id (int): The ID of the media translation to delete.
            language_code (str): The language code of the media translation to delete.
            session (Session): Database session dependency.

        Returns:
            None: Returns no content.

        Raises:
            HTTPException: 404 if the media translation is not found.
            HTTPException: 500 if there is an error deleting the media translation.
        """
        try:
            media_translation_service.delete(session, media_translation_id, language_code)
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=404, detail=(f"Resource not found: {e}"))
        except Exception as e:
            raise HTTPException(status_code=500, detail=(f"Error deleting media translation with ID {media_translation_id} and language code {language_code}: {e}"))

    return router