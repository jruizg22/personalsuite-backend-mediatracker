from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy import Select, asc, desc
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption
from sqlmodel import Session, select

from media_tracker.custom_types import OrderByType
from media_tracker.models.yt import YTVideo, YTVideoPublic, YTVideoPublicWithVisualizations, YTVideoPublicWithPlaylists, \
    YTVideoPublicWithChannel, YTVideoFull, YTVideoCreate, YTVideoUpdate, YTPlaylistVideo, YTPlaylistPublic, \
    YTVideoVisualizationPublic, YTChannelPublic, YTVideoPlaylistDetailed, YTPlaylistVideoDetailed
from media_tracker.responses.youtube_responses import YTVideoResponse, YTVideoResponseItem
from media_tracker.views.youtube_views import YTVideoView


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 100,
        order_by: OrderByType = OrderByType.ASC,
        view: YTVideoView = YTVideoView.BASIC
) -> YTVideoResponse:
    """
    Retrieve a list of YouTube video entries from the database with optional filtering by detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        order_by (OrderByType): Sorting order for the results (ascending or descending).
        view (YTVideoView): Determines the level of detail for each YouTube video entry.

    Returns:
        YTVideoResponse: A list of YouTube video entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(YTVideo)

        # Apply sorting by title (case-insensitive recommended for consistency)
        if order_by == OrderByType.ASC:
            query = query.order_by(asc(YTVideo.title))
        else:
            query = query.order_by(desc(YTVideo.title))

        # Set the level of detail requested
        query: Select = set_yt_video_detail_level(query, view)

        # Retrieve all the YouTube video with the configuration set in the previous steps
        yt_video_list: list[YTVideo] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[YTVideoResponseItem] = [set_yt_video_response_model(yt_video, view) for yt_video in yt_video_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_all_by_channel_id(
        channel_id: str,
        session: Session,
        offset: int = 0,
        limit: int = 100,
        order_by: OrderByType = OrderByType.ASC
) -> list[YTVideoPublic]:
    """
    Retrieve a list of YouTube video entries for a specific channel.

    Args:
        channel_id (str): The unique identifier of the YouTube channel.
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        order_by (OrderByType): Sorting order for the results (ascending or descending).

    Returns:
        list[YTVideoPublic]: A list of YouTube video entries from the specified channel,
                             each serialized as a public-facing model.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """
    try:
        # Base query with filter
        query = select(YTVideo).where(YTVideo.channel_id == channel_id)

        # Apply sorting by title (case-insensitive recommended for consistency)
        if order_by == OrderByType.ASC:
            query = query.order_by(asc(YTVideo.title))
        else:
            query = query.order_by(desc(YTVideo.title))

        # Apply pagination
        query = query.offset(offset).limit(limit if limit > 0 else None)

        # Execute query
        yt_video_list: list[YTVideo] = session.exec(query).all()  # type: ignore[arg-type]

        # Map results to public model
        response_model: list[YTVideoPublic] = [
            YTVideoPublic.model_validate(video) for video in yt_video_list
        ]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, yt_video_id: str, view: YTVideoView = YTVideoView.BASIC) -> YTVideoResponseItem:
    """
    Retrieve a single YouTube video entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_video_id (str): The ID of the YouTube video entry to retrieve.
        view (YTVideoView): Determines the level of detail for the YouTube video entry.

    Returns:
        YTVideoResponseItem: The requested YouTube video entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the YouTube video entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id
        query: Select = select(YTVideo).where(YTVideo.id == yt_video_id)

        # Set the level of detail requested
        query: Select = set_yt_video_detail_level(query, view)

        # Retrieve the YouTube video with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        yt_video_db: YTVideo | None = session.exec(query).first()
        if not yt_video_db:
            raise ResourceNotFoundError(f"YTVideo with ID {yt_video_id} not found")

        # Encase the item in the requested model
        response_model = set_yt_video_response_model(yt_video_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_yt_video: YTVideoCreate) -> YTVideoPublic:
    """
    Create a new YouTube video entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_yt_video (YTVideoCreate): Input data for creating a new YouTube video entry.

    Returns:
        YTVideoPublic: The newly created YouTube video entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        yt_video: YTVideo = YTVideo(**new_yt_video.model_dump())

        # Add the record to the session
        session.add(yt_video)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(yt_video)
        return YTVideoPublic.model_validate(yt_video)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, yt_video_id: str, yt_video_in: YTVideoUpdate) -> YTVideoPublic:
    """
    Update an existing YouTube video entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_video_id (str): The ID of the YouTube video entry to update.
        yt_video_in (YTVideoUpdate): Partial data for updating the YouTube video entry.

    Returns:
        YTVideoPublic: The updated YouTube video entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the YouTube video entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_video_db: YTVideo = session.get(YTVideo, yt_video_id) # type: ignore[arg-type]
        if not yt_video_db:
            raise ResourceNotFoundError(f"YouTube video with ID {yt_video_id} not found")

        # Retrieve the input data to update the necessary fields
        yt_video_data: dict[str, Any] = yt_video_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        yt_video_db.sqlmodel_update(yt_video_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(yt_video_db)

        return YTVideoPublic.model_validate(yt_video_db)
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

def delete(session: Session, yt_video_id: str) -> None:
    """
    Delete a YouTube video entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        yt_video_id (str): The ID of the YouTube video entry to delete.

    Raises:
        ResourceNotFoundError: If the YouTube video entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        yt_video: YTVideo = session.get(YTVideo, yt_video_id) # type: ignore[arg-type]
        if not yt_video:
            raise ResourceNotFoundError(f"YTVideo with ID {yt_video_id} not found")

        # Delete the record
        session.delete(yt_video)

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

def set_yt_video_detail_level(query: Select, view: YTVideoView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (YTVideoView): The desired detail level for YouTube video visualization entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view in (YTVideoView.WITH_VISUALIZATIONS, YTVideoView.FULL):
        options_list.append(selectinload(YTVideo.visualizations)) # type: ignore[arg-type]
    if view in (YTVideoView.WITH_PLAYLISTS, YTVideoView.FULL):
        options_list.append(
            selectinload(YTVideo.playlists).selectinload(YTPlaylistVideo.playlist) # type: ignore[arg-type]
        )
    if view in (YTVideoView.WITH_CHANNEL, YTVideoView.FULL):
        options_list.append(selectinload(YTVideo.channel))  # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_yt_video_response_model(yt_video: YTVideo, view: YTVideoView) -> YTVideoResponseItem:
    """
    Serialize a single YTVideo instance into the appropriate response model based on the requested view.

    Args:
        yt_video (YTVideo): The YTVideo instance to serialize.
        view (YTVideoView): The desired view for serialization.

    Returns:
        YTVideoPublic: The serialized YouTube video visualization instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case YTVideoView.BASIC:
            return YTVideoPublic.model_validate(yt_video)
        case YTVideoView.WITH_VISUALIZATIONS:
            return YTVideoPublicWithVisualizations(
                **yt_video.model_dump(),
                visualizations=[
                    YTVideoPublic.model_validate(visualization) for visualization in yt_video.visualizations
                ]
            )
        case YTVideoView.WITH_PLAYLISTS:
            return YTVideoPublicWithPlaylists(
                **yt_video.model_dump(),
                playlists=[
                    YTPlaylistVideoDetailed(
                        playlist=YTPlaylistPublic.model_validate(assoc.playlist),
                        position=assoc.position
                    )
                    for assoc in yt_video.playlists
                ]
            )
        case YTVideoView.WITH_CHANNEL:
            return YTVideoPublicWithChannel.model_validate(yt_video)
        case YTVideoView.FULL:
            return YTVideoFull(
                **yt_video.model_dump(),
                visualizations=[
                    YTVideoVisualizationPublic.model_validate(visualization) for visualization in yt_video.visualizations
                ],
                playlists=[
                    YTVideoPlaylistDetailed(
                        playlist=YTPlaylistPublic.model_validate(assoc.playlist),
                        position=assoc.position,
                    )
                    for assoc in yt_video.playlists
                ],
                channel=YTChannelPublic.model_validate(yt_video.channel)
            )
        case _:
            raise ValueError(f"Invalid view type: {view}")