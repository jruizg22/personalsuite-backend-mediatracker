from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy import Select
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption
from sqlmodel import Session, select

from media_tracker.models.yt import YTPlaylist, YTPlaylistPublic, YTPlaylistPublicWithChannel, YTPlaylistFull, \
    YTPlaylistCreate, YTPlaylistUpdate, YTPlaylistPublicWithVideos, YTPlaylistVideo, YTVideoPublic, YTChannelPublic, \
    YTPlaylistVideoDetailed
from media_tracker.responses.youtube_responses import YTPlaylistResponse, YTPlaylistResponseItem
from media_tracker.views.youtube_views import YTPlaylistView


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 0,
        view: YTPlaylistView = YTPlaylistView.BASIC
) -> YTPlaylistResponse:
    """
    Retrieve a list of YouTube playlist entries from the database with optional filtering by detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (YTPlaylistView): Determines the level of detail for each YouTube playlist entry.

    Returns:
        YTPlaylistResponse: A list of YouTube playlist entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(YTPlaylist)

        # Set the level of detail requested
        query: Select = set_yt_playlist_detail_level(query, view)

        # Retrieve all the YouTube playlist with the configuration set in the previous steps
        yt_playlist_list: list[YTPlaylist] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[YTPlaylistResponseItem] = [set_yt_playlist_response_model(yt_playlist, view) for yt_playlist in yt_playlist_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, yt_playlist_id: str, view: YTPlaylistView = YTPlaylistView.BASIC) -> YTPlaylistResponseItem:
    """
    Retrieve a single YouTube playlist entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_playlist_id (str): The ID of the YouTube playlist entry to retrieve.
        view (YTPlaylistView): Determines the level of detail for the YouTube playlist entry.

    Returns:
        YTPlaylistResponseItem: The requested YouTube playlist entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the YouTube playlist entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id
        query: Select = select(YTPlaylist).where(YTPlaylist.id == yt_playlist_id)

        # Set the level of detail requested
        query: Select = set_yt_playlist_detail_level(query, view)

        # Retrieve the YouTube playlist with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        yt_playlist_db: YTPlaylist | None = session.exec(query).first()
        if not yt_playlist_db:
            raise ResourceNotFoundError(f"YTPlaylist with ID {yt_playlist_id} not found")

        # Encase the item in the requested model
        response_model = set_yt_playlist_response_model(yt_playlist_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_yt_playlist: YTPlaylistCreate) -> YTPlaylistPublic:
    """
    Create a new YouTube playlist entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_yt_playlist (YTPlaylistCreate): Input data for creating a new YouTube playlist entry.

    Returns:
        YTPlaylistPublic: The newly created YouTube playlist entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        yt_playlist: YTPlaylist = YTPlaylist(**new_yt_playlist.model_dump())

        # Add the record to the session
        session.add(yt_playlist)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(yt_playlist)
        return YTPlaylistPublic.model_validate(yt_playlist)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, yt_playlist_id: str, yt_playlist_in: YTPlaylistUpdate) -> YTPlaylistPublic:
    """
    Update an existing YouTube playlist entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_playlist_id (str): The ID of the YouTube playlist entry to update.
        yt_playlist_in (YTPlaylistUpdate): Partial data for updating the YouTube playlist entry.

    Returns:
        YTPlaylistPublic: The updated YouTube playlist entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the YouTube playlist entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_playlist_db: YTPlaylist = session.get(YTPlaylist, yt_playlist_id) # type: ignore[arg-type]
        if not yt_playlist_db:
            raise ResourceNotFoundError(f"YouTube playlist with ID {yt_playlist_id} not found")

        # Retrieve the input data to update the necessary fields
        yt_playlist_data: dict[str, Any] = yt_playlist_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        yt_playlist_db.sqlmodel_update(yt_playlist_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(yt_playlist_db)

        return YTPlaylistPublic.model_validate(yt_playlist_db)
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

def delete(session: Session, yt_playlist_id: str) -> None:
    """
    Delete a YouTube playlist entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_playlist_id (str): The ID of the YouTube playlist entry to delete.

    Raises:
        ResourceNotFoundError: If the YouTube playlist entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_playlist: YTPlaylist = session.get(YTPlaylist, yt_playlist_id) # type: ignore[arg-type]
        if not yt_playlist:
            raise ResourceNotFoundError(f"YTPlaylist with ID {yt_playlist_id} not found")

        # Delete the record
        session.delete(yt_playlist)

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

def set_yt_playlist_detail_level(query: Select, view: YTPlaylistView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (YTPlaylistView): The desired detail level for YouTube playlist visualization entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view in (YTPlaylistView.WITH_VIDEOS, YTPlaylistView.FULL):
        options_list.append(
            selectinload(YTPlaylist.videos).selectinload(YTPlaylistVideo.video) # type: ignore[arg-type]
        )
    if view in (YTPlaylistView.WITH_CHANNEL, YTPlaylistView.FULL):
        options_list.append(selectinload(YTPlaylist.channel))  # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_yt_playlist_response_model(yt_playlist: YTPlaylist, view: YTPlaylistView) -> YTPlaylistResponseItem:
    """
    Serialize a single YTPlaylist instance into the appropriate response model based on the requested view.

    Args:
        yt_playlist (YTPlaylist): The YTPlaylist instance to serialize.
        view (YTPlaylistView): The desired view for serialization.

    Returns:
        YTPlaylistPublic: The serialized YouTube playlist visualization instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case YTPlaylistView.BASIC:
            return YTPlaylistPublic.model_validate(yt_playlist)
        case YTPlaylistView.WITH_VIDEOS:
            return YTPlaylistPublicWithVideos(
                **yt_playlist.model_dump(),
                videos=[
                    YTPlaylistVideoDetailed(
                        video=YTVideoPublic.model_validate(assoc.video),
                        position=assoc.position
                    )
                    for assoc in yt_playlist.videos
                ]
            )
        case YTPlaylistView.WITH_CHANNEL:
            return YTPlaylistPublicWithChannel.model_validate(yt_playlist)
        case YTPlaylistView.FULL:
            return YTPlaylistFull(
                **yt_playlist.model_dump(),
                channel=YTChannelPublic.model_validate(yt_playlist.channel),
                videos=[
                    YTPlaylistVideoDetailed(
                        video=YTVideoPublic.model_validate(assoc.video),
                        position=assoc.position
                    )
                    for assoc in yt_playlist.videos
                ]
            )
        case _:
            raise ValueError(f"Invalid view type: {view}")