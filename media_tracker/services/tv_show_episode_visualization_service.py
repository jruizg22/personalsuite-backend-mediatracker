from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption
from sqlalchemy.sql import Select
from sqlmodel import Session, select

from media_tracker.misc.responses import TVShowEpisodeVisualizationResponse, TVShowEpisodeVisualizationResponseItem
from media_tracker.misc.views import TVShowEpisodeVisualizationView
from media_tracker.models.media import TVShowEpisodeVisualizationPublic, TVShowEpisodeVisualizationPublicWithEpisode, TVShowEpisodeVisualization, \
    TVShowEpisodeVisualizationCreate, TVShowEpisodeVisualizationUpdate


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 0,
        view: TVShowEpisodeVisualizationView = TVShowEpisodeVisualizationView.BASIC
) -> TVShowEpisodeVisualizationResponse:
    """
    Retrieve a list of TV show episode visualization entries from the database with optional filtering by media type and detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (TVShowEpisodeVisualizationView): Determines the level of detail for each TV show episode visualization entry.

    Returns:
        TVShowEpisodeVisualizationResponse: A list of TV show episode visualization entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(TVShowEpisodeVisualization)

        # Set the level of detail requested
        query: Select = set_tv_show_episode_visualization_detail_level(query, view)

        # Retrieve all the media with the configuration set in the previous steps
        tv_show_episode_visualization_list: list[TVShowEpisodeVisualization] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[TVShowEpisodeVisualizationResponseItem] = [set_tv_show_episode_visualization_response_model(tv_show_episode_visualization, view) for tv_show_episode_visualization in tv_show_episode_visualization_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, tv_show_episode_visualization_id: int, view: TVShowEpisodeVisualizationView = TVShowEpisodeVisualizationView.BASIC) -> TVShowEpisodeVisualizationResponseItem:
    """
    Retrieve a single TV show episode visualization entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        tv_show_episode_visualization_id (int): The ID of the TV show episode visualization entry to retrieve.
        view (TVShowEpisodeVisualizationView): Determines the level of detail for the TV show episode visualization entry.

    Returns:
        TVShowEpisodeVisualizationResponseItem: The requested TV show episode visualization entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the TV show episode visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id
        query: Select = select(TVShowEpisodeVisualization).where(TVShowEpisodeVisualization.id == tv_show_episode_visualization_id)

        # Set the level of detail requested
        query: Select = set_tv_show_episode_visualization_detail_level(query, view)

        # Retrieve the media with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        tv_show_episode_visualization_db: TVShowEpisodeVisualization | None = session.exec(query).first()
        if not tv_show_episode_visualization_db:
            raise ResourceNotFoundError(f"TVShowEpisodeVisualization with ID {tv_show_episode_visualization_id} not found")

        # Encase the item in the requested model
        response_model = set_tv_show_episode_visualization_response_model(tv_show_episode_visualization_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_tv_show_episode_visualization: TVShowEpisodeVisualizationCreate) -> TVShowEpisodeVisualizationPublic:
    """
    Create a new TV show episode visualization entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_tv_show_episode_visualization (TVShowEpisodeVisualizationCreate): Input data for creating a new TV show episode visualization entry.

    Returns:
        TVShowEpisodeVisualizationPublic: The newly created TV show episode visualization entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        tv_show_episode_visualization: TVShowEpisodeVisualization = TVShowEpisodeVisualization(**new_tv_show_episode_visualization.model_dump())

        # Add the record to the session
        session.add(tv_show_episode_visualization)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(tv_show_episode_visualization)
        return TVShowEpisodeVisualizationPublic.model_validate(tv_show_episode_visualization)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, tv_show_episode_visualization_id: int, tv_show_episode_visualization_in: TVShowEpisodeVisualizationUpdate) -> TVShowEpisodeVisualizationPublic:
    """
    Update an existing TV show episode visualization entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        tv_show_episode_visualization_id (int): The ID of the TV show episode visualization entry to update.
        tv_show_episode_visualization_in (TVShowEpisodeVisualizationUpdate): Partial data for updating the TV show episode visualization entry.

    Returns:
        TVShowEpisodeVisualization: The updated TV show episode visualization entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the TV show episode visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        tv_show_episode_visualization_db: TVShowEpisodeVisualization = session.get(TVShowEpisodeVisualization, tv_show_episode_visualization_id) # type: ignore[arg-type]
        if not tv_show_episode_visualization_db:
            raise ResourceNotFoundError(f"TVShowEpisodeVisualization with ID {tv_show_episode_visualization_id} not found")

        # Retrieve the input data to update the necessary fields
        tv_show_episode_visualization_data: dict[str, Any] = tv_show_episode_visualization_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        media_db.sqlmodel_update(tv_show_episode_visualization_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(tv_show_episode_visualization_db)

        return TVShowEpisodeVisualizationPublic.model_validate(tv_show_episode_visualization_db)
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

def delete(session: Session, tv_show_episode_visualization_id: int) -> None:
    """
    Delete a TV show episode visualization entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        tv_show_episode_visualization_id (int): The ID of the TV show episode visualization entry to delete.

    Raises:
        ResourceNotFoundError: If the TV show episode visualization entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        tv_show_episode_visualization: TVShowEpisodeVisualization = session.get(TVShowEpisodeVisualization, tv_show_episode_visualization_id) # type: ignore[arg-type]
        if not tv_show_episode_visualization:
            raise ResourceNotFoundError(f"TVShowEpisodeVisualization with ID {tv_show_episode_visualization_id} not found")

        # Delete the record
        session.delete(tv_show_episode_visualization)

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

def set_tv_show_episode_visualization_detail_level(query: Select, view: TVShowEpisodeVisualizationView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (TVShowEpisodeVisualizationView): The desired detail level for TV show episode visualization entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view == TVShowEpisodeVisualizationView.WITH_EPISODE:
        options_list.append(selectinload(TVShowEpisodeVisualization.episode)) # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_tv_show_episode_visualization_response_model(tv_show_episode_visualization: TVShowEpisodeVisualization, view: TVShowEpisodeVisualizationView) -> TVShowEpisodeVisualizationPublic | TVShowEpisodeVisualizationPublicWithEpisode:
    """
    Serialize a single TVShowEpisodeVisualization instance into the appropriate response model based on the requested view.

    Args:
        tv_show_episode_visualization (TVShowEpisodeVisualization): The TVShowEpisodeVisualization instance to serialize.
        view (TVShowEpisodeVisualizationView): The desired view for serialization.

    Returns:
        TVShowEpisodeVisualizationPublic: The serialized TV show episode visualization instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case TVShowEpisodeVisualizationView.BASIC:
            return TVShowEpisodeVisualizationPublic.model_validate(tv_show_episode_visualization)
        case TVShowEpisodeVisualizationView.WITH_EPISODE:
            return TVShowEpisodeVisualizationPublicWithEpisode.model_validate(tv_show_episode_visualization)
        case _:
            raise ValueError(f"Invalid view type: {view}")