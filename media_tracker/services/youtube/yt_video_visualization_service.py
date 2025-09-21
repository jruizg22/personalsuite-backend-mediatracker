from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy import Select
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm.interfaces import LoaderOption
from sqlmodel import Session, select

from media_tracker.models.yt import YTVideoVisualization, YTVideoVisualizationPublic, YTVideoVisualizationCreate, \
    YTVideoVisualizationUpdate, YTVideoVisualizationPublicWithVideo
from media_tracker.responses.youtube_responses import YTVideoVisualizationResponse, YTVideoVisualizationResponseItem
from media_tracker.views.youtube_views import YTVideoVisualizationView


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 0,
        view: YTVideoVisualizationView = YTVideoVisualizationView.BASIC
) -> YTVideoVisualizationResponse:
    """
    Retrieve a list of YouTube video visualization entries from the database with optional filtering by detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (YTVideoVisualizationView): Determines the level of detail for each YouTube video visualization entry.

    Returns:
        YTVideoVisualizationResponse: A list of YouTube video visualization entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(YTVideoVisualization)

        # Set the level of detail requested
        query: Select = set_yt_video_visualization_detail_level(query, view)

        # Retrieve all the YouTube video visualization with the configuration set in the previous steps
        yt_video_visualization_list: list[YTVideoVisualization] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[YTVideoVisualizationResponseItem] = [set_yt_video_visualization_response_model(yt_video_visualization, view) for yt_video_visualization in yt_video_visualization_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, yt_video_visualization_id: int, view: YTVideoVisualizationView = YTVideoVisualizationView.BASIC) -> YTVideoVisualizationResponseItem:
    """
    Retrieve a single YouTube video visualization entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_video_visualization_id (int): The ID of the YouTube video visualization entry to retrieve.
        view (YTVideoVisualizationView): Determines the level of detail for the YouTube video visualization entry.

    Returns:
        YTVideoVisualizationResponseItem: The requested YouTube video visualization entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the YouTube video visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id
        query: Select = select(YTVideoVisualization).where(YTVideoVisualization.id == yt_video_visualization_id)

        # Set the level of detail requested
        query: Select = set_yt_video_visualization_detail_level(query, view)

        # Retrieve the YouTube video visualization with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        yt_video_visualization_db: YTVideoVisualization | None = session.exec(query).first()
        if not yt_video_visualization_db:
            raise ResourceNotFoundError(f"YTVideoVisualization with ID {yt_video_visualization_id} not found")

        # Encase the item in the requested model
        response_model = set_yt_video_visualization_response_model(yt_video_visualization_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_yt_video_visualization: YTVideoVisualizationCreate) -> YTVideoVisualizationPublic:
    """
    Create a new YouTube video visualization entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_yt_video_visualization (YTVideoVisualizationCreate): Input data for creating a new YouTube video visualization entry.

    Returns:
        YTVideoVisualizationPublic: The newly created YouTube video visualization entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        yt_video_visualization: YTVideoVisualization = YTVideoVisualization(**new_yt_video_visualization.model_dump())

        # Add the record to the session
        session.add(yt_video_visualization)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(yt_video_visualization)
        return YTVideoVisualizationPublic.model_validate(yt_video_visualization)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, yt_video_visualization_id: int, yt_video_visualization_in: YTVideoVisualizationUpdate) -> YTVideoVisualizationPublic:
    """
    Update an existing YouTube video visualization entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_video_visualization_id (int): The ID of the YouTube video visualization entry to update.
        yt_video_visualization_in (YTVideoVisualizationUpdate): Partial data for updating the YouTube video visualization entry.

    Returns:
        YTVideoVisualizationPublic: The updated YouTube video visualization entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the YouTube video visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_video_visualization_db: YTVideoVisualization = session.get(YTVideoVisualization, yt_video_visualization_id) # type: ignore[arg-type]
        if not yt_video_visualization_db:
            raise ResourceNotFoundError(f"YouTube video visualization with ID {yt_video_visualization_id} not found")

        # Retrieve the input data to update the necessary fields
        yt_video_visualization_data: dict[str, Any] = yt_video_visualization_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        yt_video_visualization_db.sqlmodel_update(yt_video_visualization_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(yt_video_visualization_db)

        return YTVideoVisualizationPublic.model_validate(yt_video_visualization_db)
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

def delete(session: Session, yt_video_visualization_id: int) -> None:
    """
    Delete a YouTube video visualization entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_video_visualization_id (int): The ID of the YouTube video visualization entry to delete.

    Raises:
        ResourceNotFoundError: If the YouTube video visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_video_visualization: YTVideoVisualization = session.get(YTVideoVisualization, yt_video_visualization_id) # type: ignore[arg-type]
        if not yt_video_visualization:
            raise ResourceNotFoundError(f"YTVideoVisualization with ID {yt_video_visualization_id} not found")

        # Delete the record
        session.delete(yt_video_visualization)

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
    
def set_yt_video_visualization_detail_level(query: Select, view: YTVideoVisualizationView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (YTVideoVisualizationView): The desired detail level for YouTube video visualization entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view == YTVideoVisualizationView.WITH_VIDEO:
        options_list.append(selectinload(YTVideoVisualization.video)) # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_yt_video_visualization_response_model(yt_video_visualization: YTVideoVisualization, view: YTVideoVisualizationView) -> YTVideoVisualizationResponseItem:
    """
    Serialize a single YTVideoVisualization instance into the appropriate response model based on the requested view.

    Args:
        yt_video_visualization (YTVideoVisualization): The YTVideoVisualization instance to serialize.
        view (YTVideoVisualizationView): The desired view for serialization.

    Returns:
        YTVideoVisualizationPublic: The serialized YouTube video visualization instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case YTVideoVisualizationView.BASIC:
            return YTVideoVisualizationPublic.model_validate(yt_video_visualization)
        case YTVideoVisualizationView.WITH_VIDEO:
            return YTVideoVisualizationPublicWithVideo.model_validate(yt_video_visualization)
        case _:
            raise ValueError(f"Invalid view type: {view}")