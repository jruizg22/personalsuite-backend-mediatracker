from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption
from sqlalchemy.sql import Select
from sqlmodel import Session, select, and_

from media_tracker.responses.media_responses import MediaTranslationResponse, MediaTranslationResponseItem
from media_tracker.views.media_views import MediaTranslationView
from media_tracker.models.media import MediaTranslationPublic, MediaTranslationPublicWithMedia, MediaTranslation, \
    MediaTranslationCreate, MediaTranslationUpdate


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 0,
        view: MediaTranslationView = MediaTranslationView.BASIC
) -> MediaTranslationResponse:
    """
    Retrieve a list of media translation entries from the database with optional filtering by detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (MediaTranslationView): Determines the level of detail for each media translation entry.

    Returns:
        MediaTranslationResponse: A list of media translation entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(MediaTranslation)

        # Set the level of detail requested
        query: Select = set_media_translation_detail_level(query, view)

        # Retrieve all the media with the configuration set in the previous steps
        media_translation_list: list[MediaTranslation] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[MediaTranslationResponseItem] = [set_media_translation_response_model(media_translation, view) for media_translation in media_translation_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, media_translation_id: int, language_code: str = None, view: MediaTranslationView = MediaTranslationView.BASIC) -> MediaTranslationResponseItem:
    """
    Retrieve a single media translation entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_translation_id (int): The ID of the media translation entry to retrieve.
        language_code (str): The language code of the media translation entry to retrieve. If left None, all the translations with the same ID will be retrieved.
        view (MediaTranslationView): Determines the level of detail for the media translation entry.

    Returns:
        MediaTranslationResponseItem: The requested media translation entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the media translation entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id and language code, if necessary
        if not language_code:
            query: Select = select(MediaTranslation).where(MediaTranslation.media_id == media_translation_id)
        else:
            query: Select = select(MediaTranslation).where(
                and_(
                    MediaTranslation.media_id == media_translation_id,
                    MediaTranslation.language_code == language_code
                )
            )

        # Set the level of detail requested
        query: Select = set_media_translation_detail_level(query, view)

        # Retrieve the media with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        media_translation_db: MediaTranslation | None = session.exec(query).first()
        if not media_translation_db:
            if not language_code:
                raise ResourceNotFoundError(f"MediaTranslation with ID {media_translation_id} not found")
            else:
                raise ResourceNotFoundError(f"MediaTranslation with ID {media_translation_id} and language code {language_code} not found")

        # Encase the item in the requested model
        response_model = set_media_translation_response_model(media_translation_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_media_translation: MediaTranslationCreate) -> MediaTranslationPublic:
    """
    Create a new media translation entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_media_translation (MediaTranslationCreate): Input data for creating a new media translation entry.

    Returns:
        MediaTranslationPublic: The newly created media translation entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        media_translation: MediaTranslation = MediaTranslation(**new_media_translation.model_dump())

        # Add the record to the session
        session.add(media_translation)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(media_translation)
        return MediaTranslationPublic.model_validate(media_translation)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, media_translation_id: int, language_code: str, media_translation_in: MediaTranslationUpdate) -> MediaTranslationPublic:
    """
    Update an existing media translation entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_translation_id (int): The ID of the media translation entry to update.
        language_code (str): The language code of the media translation entry to update.
        media_translation_in (MediaTranslationUpdate): Partial data for updating the media translation entry.

    Returns:
        MediaTranslation: The updated media translation entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the media translation entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        media_translation_db: MediaTranslation = session.get(MediaTranslation, (media_translation_id, language_code))  # type: ignore[arg-type]
        if not media_translation_db:
            raise ResourceNotFoundError(f"MediaTranslation with ID {media_translation_id} and language code {language_code} not found")

        # Retrieve the input data to update the necessary fields
        media_translation_data: dict[str, Any] = media_translation_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        media_db.sqlmodel_update(media_translation_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(media_translation_db)

        return MediaTranslationPublic.model_validate(media_translation_db)
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def delete(session: Session, media_translation_id: int, language_code: str) -> None:
    """
    Delete a media translation entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_translation_id (int): The ID of the media translation entry to delete.
        language_code (str): The language code of the media translation entry to delete.

    Raises:
        ResourceNotFoundError: If the media translation entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        media_translation: MediaTranslation = session.get(MediaTranslation, (media_translation_id, language_code)) # type: ignore[arg-type]
        if not media_translation:
            raise ResourceNotFoundError(f"MediaTranslation with ID {media_translation_id} and language code {language_code} not found")

        # Delete the record
        session.delete(media_translation)

        # Save the changes to the database
        session.commit()
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def set_media_translation_detail_level(query: Select, view: MediaTranslationView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (MediaTranslationView): The desired detail level for media translation entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view == MediaTranslationView.WITH_MEDIA:
        options_list.append(selectinload(MediaTranslation.media)) # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_media_translation_response_model(media_translation: MediaTranslation, view: MediaTranslationView) -> MediaTranslationPublic | MediaTranslationPublicWithMedia:
    """
    Serialize a single MediaTranslation instance into the appropriate response model based on the requested view.

    Args:
        media_translation (MediaTranslation): The MediaTranslation instance to serialize.
        view (MediaTranslationView): The desired view for serialization.

    Returns:
        MediaTranslationPublic: The serialized media translation instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case MediaTranslationView.BASIC:
            return MediaTranslationPublic.model_validate(media_translation)
        case MediaTranslationView.WITH_MEDIA:
            return MediaTranslationPublicWithMedia.model_validate(media_translation)
        case _:
            raise ValueError(f"Invalid view type: {view}")