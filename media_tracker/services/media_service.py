from typing import Any, Optional

from pydantic import ValidationError
from sqlalchemy.orm.interfaces import LoaderOption
from sqlalchemy.sql import Select
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError # type: ignore

from media_tracker.models.media import *


def get_all(session: Session, media_type: Optional[MediaType], offset: int = 0, limit: int = 0, view: MediaView = MediaView.BASIC) -> MediaResponse:
    """
    Retrieve a list of media entries from the database with optional filtering by media type and detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_type (Optional[MediaType]): Filter by media type (movie, TV show, other). If None, retrieves all types.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (MediaView): Determines the level of detail for each media entry.

    Returns:
        MediaResponse: A list of media entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(Media)

        # Filter by media type
        query: Select = set_media_type(query, media_type)

        # Set the level of detail requested
        query: Select = set_media_detail_level(query, view, media_type)

        # Retrieve all the media with the configuration set in the previous steps
        media_list: list[Media] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[MediaResponseItem] = [set_media_response_model(media, view) for media in media_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, media_id: int, view: MediaView = MediaView.BASIC) -> MediaResponseItem:
    """
    Retrieve a single media entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_id (int): The ID of the media entry to retrieve.
        view (MediaView): Determines the level of detail for the media entry.

    Returns:
        MediaResponseItem: The requested media entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the media entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id
        query: Select = select(Media).where(Media.id == media_id)

        # Set the level of detail requested
        query: Select = set_media_detail_level(query, view)

        # Retrieve the media with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        media_db: Media | None = session.exec(query).first()
        if not media_db:
            raise ResourceNotFoundError(f"Media with ID {media_id} not found")

        # Encase the item in the requested model
        response_model = set_media_response_model(media_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_media: MediaCreate) -> MediaPublic:
    """
    Create a new media entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_media (MediaCreate): Input data for creating a new media entry.

    Returns:
        MediaPublic: The newly created media entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        media: Media = Media(**new_media.model_dump())

        # Add the record to the session
        session.add(media)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(media)
        return MediaPublic.model_validate(media)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, media_id: int, media_in: MediaUpdate) -> MediaPublic:
    """
    Update an existing media entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_id (int): The ID of the media entry to update.
        media_in (MediaUpdate): Partial data for updating the media entry.

    Returns:
        MediaPublic: The updated media entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the media entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        media_db: Media = session.get(Media, media_id) # type: ignore[arg-type]
        if not media_db:
            raise ResourceNotFoundError(f"Media with ID {media_id} not found")

        # Retrieve the input data to update the necessary fields
        media_data: dict[str, Any] = media_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        media_db.sqlmodel_update(media_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(media_db)

        return MediaPublic.model_validate(media_db)
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

def delete(session: Session, media_id: int) -> None:
    """
    Delete a media entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_id (int): The ID of the media entry to delete.

    Raises:
        ResourceNotFoundError: If the media entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        media: Media = session.get(Media, media_id) # type: ignore[arg-type]
        if not media:
            raise ResourceNotFoundError(f"Media with ID {media_id} not found")

        # Delete the record
        session.delete(media)

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

def set_media_type(query: Select, media_type: MediaType) -> Select:
    """
    Apply a media type filter to the query.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        media_type (MediaType): The media type to filter by.

    Returns:
        Select: The updated query with the applied media type filter.

    Raises:
        ValueError: If an invalid media type is provided.
    """

    match media_type:
        case MediaType.MOVIE:
            return query.where(Media.type == MediaType.MOVIE) # type: ignore[arg-type]
        case MediaType.TV_SHOW:
            return query.where(Media.type == MediaType.TV_SHOW) # type: ignore[arg-type]
        case MediaType.OTHER:
            return query.where(Media.type == MediaType.OTHER) # type: ignore[arg-type]
        case None:
            return query
        case _:
            raise ValueError(f"Invalid media type: {media_type}")

def set_media_detail_level(query: Select, view: MediaView, media_type: Optional[MediaType] = None) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (MediaView): The desired detail level for media entries.
        media_type (MediaType, optional): Used to conditionally load TV show episodes.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view in (MediaView.WITH_TRANSLATIONS, MediaView.FULL, MediaView.FULL_WITH_TV_SHOW_EPISODES):
        options_list.append(selectinload(Media.translations)) # type: ignore[arg-type]
    if view in (MediaView.WITH_VISUALIZATIONS, MediaView.FULL, MediaView.FULL_WITH_TV_SHOW_EPISODES):
        options_list.append(selectinload(Media.visualizations)) # type: ignore[arg-type]
    if view == MediaView.FULL_WITH_TV_SHOW_EPISODES and media_type == MediaType.TV_SHOW:
        options_list.append(selectinload(Media.tv_show_episodes)) # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_media_response_model(media: Media, view: MediaView) -> MediaResponseItem:
    """
    Serialize a single Media instance into the appropriate response model based on the requested view.

    Args:
        media (Media): The Media instance to serialize.
        view (MediaView): The desired view for serialization.

    Returns:
        MediaResponseItem: The serialized media instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case MediaView.BASIC:
            return MediaPublic.model_validate(media)
        case MediaView.WITH_TRANSLATIONS:
            return MediaPublicWithTranslations.model_validate(media)
        case MediaView.WITH_VISUALIZATIONS:
            return MediaPublicWithVisualizations.model_validate(media)
        case MediaView.FULL:
            return MediaFull.model_validate(media)
        case MediaView.FULL_WITH_TV_SHOW_EPISODES:
            return MediaFullWithTVShowEpisodes.model_validate(media)
        case _:
            raise ValueError(f"Invalid view type: {view}")