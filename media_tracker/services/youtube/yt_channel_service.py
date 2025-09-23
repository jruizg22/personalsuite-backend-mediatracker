from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy import Select
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption
from sqlmodel import Session, select

from media_tracker.models.yt import YTChannel, YTChannelPublic, YTChannelPublicWithVideos, YTChannelPublicWithPlaylists, \
    YTChannelFull, YTChannelCreate, YTChannelUpdate
from media_tracker.responses.youtube_responses import YTChannelResponse, YTChannelResponseItem
from media_tracker.views.youtube_views import YTChannelView


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 0,
        view: YTChannelView = YTChannelView.BASIC
) -> YTChannelResponse:
    """
    Retrieve a list of YouTube channel entries from the database with optional filtering by detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (YTChannelView): Determines the level of detail for each YouTube channel entry.

    Returns:
        YTChannelResponse: A list of YouTube channel entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(YTChannel)

        # Set the level of detail requested
        query: Select = set_yt_channel_detail_level(query, view)

        # Retrieve all the YouTube channel with the configuration set in the previous steps
        yt_channel_list: list[YTChannel] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[YTChannelResponseItem] = [set_yt_channel_response_model(yt_channel, view) for yt_channel in yt_channel_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, yt_channel_id: str, view: YTChannelView = YTChannelView.BASIC) -> YTChannelResponseItem:
    """
    Retrieve a single YouTube channel entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_channel_id (int): The ID of the YouTube channel entry to retrieve.
        view (YTChannelView): Determines the level of detail for the YouTube channel entry.

    Returns:
        YTChannelResponseItem: The requested YouTube channel entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the YouTube channel entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id
        query: Select = select(YTChannel).where(YTChannel.id == yt_channel_id)

        # Set the level of detail requested
        query: Select = set_yt_channel_detail_level(query, view)

        # Retrieve the YouTube channel with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        yt_channel_db: YTChannel | None = session.exec(query).first()
        if not yt_channel_db:
            raise ResourceNotFoundError(f"YTChannel with ID {yt_channel_id} not found")

        # Encase the item in the requested model
        response_model = set_yt_channel_response_model(yt_channel_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_yt_channel: YTChannelCreate) -> YTChannelPublic:
    """
    Create a new YouTube channel entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_yt_channel (YTChannelCreate): Input data for creating a new YouTube channel entry.

    Returns:
        YTChannelPublic: The newly created YouTube channel entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        yt_channel: YTChannel = YTChannel(**new_yt_channel.model_dump())

        # Add the record to the session
        session.add(yt_channel)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(yt_channel)
        return YTChannelPublic.model_validate(yt_channel)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, yt_channel_id: str, yt_channel_in: YTChannelUpdate) -> YTChannelPublic:
    """
    Update an existing YouTube channel entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_channel_id (str): The ID of the YouTube channel entry to update.
        yt_channel_in (YTChannelUpdate): Partial data for updating the YouTube channel entry.

    Returns:
        YTChannelPublic: The updated YouTube channel entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the YouTube channel entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_channel_db: YTChannel = session.get(YTChannel, yt_channel_id) # type: ignore[arg-type]
        if not yt_channel_db:
            raise ResourceNotFoundError(f"YouTube channel with ID {yt_channel_id} not found")

        # Retrieve the input data to update the necessary fields
        yt_channel_data: dict[str, Any] = yt_channel_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        yt_channel_db.sqlmodel_update(yt_channel_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(yt_channel_db)

        return YTChannelPublic.model_validate(yt_channel_db)
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

def delete(session: Session, yt_channel_id: str) -> None:
    """
    Delete a YouTube channel entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_channel_id (str): The ID of the YouTube channel entry to delete.

    Raises:
        ResourceNotFoundError: If the YouTube channel entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_channel: YTChannel = session.get(YTChannel, yt_channel_id) # type: ignore[arg-type]
        if not yt_channel:
            raise ResourceNotFoundError(f"YTChannel with ID {yt_channel_id} not found")

        # Delete the record
        session.delete(yt_channel)

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

def set_yt_channel_detail_level(query: Select, view: YTChannelView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (YTChannelView): The desired detail level for YouTube channel visualization entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view in (YTChannelView.WITH_VIDEOS, YTChannelView.FULL):
        options_list.append(selectinload(YTChannel.videos)) # type: ignore[arg-type]
    if view in (YTChannelView.WITH_PLAYLISTS, YTChannelView.FULL):
        options_list.append(selectinload(YTChannel.playlists))  # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_yt_channel_response_model(yt_channel: YTChannel, view: YTChannelView) -> YTChannelResponseItem:
    """
    Serialize a single YTChannel instance into the appropriate response model based on the requested view.

    Args:
        yt_channel (YTChannel): The YTChannel instance to serialize.
        view (YTChannelView): The desired view for serialization.

    Returns:
        YTChannelPublic: The serialized YouTube channel visualization instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case YTChannelView.BASIC:
            return YTChannelPublic.model_validate(yt_channel)
        case YTChannelView.WITH_VIDEOS:
            return YTChannelPublicWithVideos.model_validate(yt_channel)
        case YTChannelView.WITH_PLAYLISTS:
            return YTChannelPublicWithPlaylists.model_validate(yt_channel)
        case YTChannelView.FULL:
            return YTChannelFull.model_validate(yt_channel)
        case _:
            raise ValueError(f"Invalid view type: {view}")