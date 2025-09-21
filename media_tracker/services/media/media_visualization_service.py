from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption
from sqlalchemy.sql import Select
from sqlmodel import Session, select

from media_tracker.responses.media_responses import MediaVisualizationResponse, MediaVisualizationResponseItem
from media_tracker.views.media_views import MediaVisualizationView
from media_tracker.models.media import MediaVisualizationPublic, MediaVisualizationPublicWithMedia, MediaVisualization, \
    MediaVisualizationCreate, MediaVisualizationUpdate


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 0,
        view: MediaVisualizationView = MediaVisualizationView.BASIC
) -> MediaVisualizationResponse:
    """
    Retrieve a list of media visualization entries from the database with optional filtering by media type and detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (MediaVisualizationView): Determines the level of detail for each media visualization entry.

    Returns:
        MediaVisualizationResponse: A list of media visualization entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(MediaVisualization)

        # Set the level of detail requested
        query: Select = set_media_visualization_detail_level(query, view)

        # Retrieve all the media with the configuration set in the previous steps
        media_visualization_list: list[MediaVisualization] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[MediaVisualizationResponseItem] = [set_media_visualization_response_model(media_visualization, view) for media_visualization in media_visualization_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, media_visualization_id: int, view: MediaVisualizationView = MediaVisualizationView.BASIC) -> MediaVisualizationResponseItem:
    """
    Retrieve a single media visualization entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_visualization_id (int): The ID of the media visualization entry to retrieve.
        view (MediaVisualizationView): Determines the level of detail for the media visualization entry.

    Returns:
        MediaVisualizationResponseItem: The requested media visualization entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the media visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id
        query: Select = select(MediaVisualization).where(MediaVisualization.id == media_visualization_id)

        # Set the level of detail requested
        query: Select = set_media_visualization_detail_level(query, view)

        # Retrieve the media with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        media_visualization_db: MediaVisualization | None = session.exec(query).first()
        if not media_visualization_db:
            raise ResourceNotFoundError(f"MediaVisualization with ID {media_visualization_id} not found")

        # Encase the item in the requested model
        response_model = set_media_visualization_response_model(media_visualization_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_media_visualization: MediaVisualizationCreate) -> MediaVisualizationPublic:
    """
    Create a new media visualization entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_media_visualization (MediaVisualizationCreate): Input data for creating a new media visualization entry.

    Returns:
        MediaVisualizationPublic: The newly created media visualization entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        media_visualization: MediaVisualization = MediaVisualization(**new_media_visualization.model_dump())

        # Add the record to the session
        session.add(media_visualization)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(media_visualization)
        return MediaVisualizationPublic.model_validate(media_visualization)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, media_visualization_id: int, media_visualization_in: MediaVisualizationUpdate) -> MediaVisualizationPublic:
    """
    Update an existing media visualization entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_visualization_id (int): The ID of the media visualization entry to update.
        media_visualization_in (MediaVisualizationUpdate): Partial data for updating the media visualization entry.

    Returns:
        MediaVisualization: The updated media visualization entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the media visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        media_visualization_db: MediaVisualization = session.get(MediaVisualization, media_visualization_id) # type: ignore[arg-type]
        if not media_visualization_db:
            raise ResourceNotFoundError(f"MediaVisualization with ID {media_visualization_id} not found")

        # Retrieve the input data to update the necessary fields
        media_visualization_data: dict[str, Any] = media_visualization_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        media_db.sqlmodel_update(media_visualization_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(media_visualization_db)

        return MediaVisualizationPublic.model_validate(media_visualization_db)
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

def delete(session: Session, media_visualization_id: int) -> None:
    """
    Delete a media visualization entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        media_visualization_id (int): The ID of the media visualization entry to delete.

    Raises:
        ResourceNotFoundError: If the media visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        media_visualization: MediaVisualization = session.get(MediaVisualization, media_visualization_id) # type: ignore[arg-type]
        if not media_visualization:
            raise ResourceNotFoundError(f"MediaVisualization with ID {media_visualization_id} not found")

        # Delete the record
        session.delete(media_visualization)

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

def set_media_visualization_detail_level(query: Select, view: MediaVisualizationView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (MediaVisualizationView): The desired detail level for media visualization entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view == MediaVisualizationView.WITH_MEDIA:
        options_list.append(selectinload(MediaVisualization.media)) # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_media_visualization_response_model(media_visualization: MediaVisualization, view: MediaVisualizationView) -> MediaVisualizationPublic | MediaVisualizationPublicWithMedia:
    """
    Serialize a single MediaVisualization instance into the appropriate response model based on the requested view.

    Args:
        media_visualization (MediaVisualization): The MediaVisualization instance to serialize.
        view (MediaVisualizationView): The desired view for serialization.

    Returns:
        MediaVisualizationPublic: The serialized media visualization instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case MediaVisualizationView.BASIC:
            return MediaVisualizationPublic.model_validate(media_visualization)
        case MediaVisualizationView.WITH_MEDIA:
            return MediaVisualizationPublicWithMedia.model_validate(media_visualization)
        case _:
            raise ValueError(f"Invalid view type: {view}")