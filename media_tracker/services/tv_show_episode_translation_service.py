from typing import Any

# The import will work when the module is installed into the core
from core.exceptions import ResourceNotFoundError  # type: ignore
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption
from sqlalchemy.sql import Select
from sqlmodel import Session, select, and_

from media_tracker.responses.media_responses import TVShowEpisodeTranslationResponse, TVShowEpisodeTranslationResponseItem
from media_tracker.views.media_views import TVShowEpisodeTranslationView
from media_tracker.models.media import TVShowEpisodeTranslationPublic, TVShowEpisodeTranslationPublicWithEpisode, TVShowEpisodeTranslation, \
    TVShowEpisodeTranslationCreate, TVShowEpisodeTranslationUpdate


def get_all(
        session: Session,
        offset: int = 0,
        limit: int = 0,
        view: TVShowEpisodeTranslationView = TVShowEpisodeTranslationView.BASIC
) -> TVShowEpisodeTranslationResponse:
    """
    Retrieve a list of TV show episode translation entries from the database with optional filtering by media type and detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        offset (int): Number of items to skip for pagination.
        limit (int): Maximum number of items to return. If 0, no limit is applied.
        view (TVShowEpisodeTranslationView): Determines the level of detail for each TV show episode translation entry.

    Returns:
        TVShowEpisodeTranslationResponse: A list of TV show episode translation entries serialized according to the specified view.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query
        query: Select = select(TVShowEpisodeTranslation)

        # Set the level of detail requested
        query: Select = set_tv_show_episode_translation_detail_level(query, view)

        # Retrieve all the media with the configuration set in the previous steps
        tv_show_episode_translation_list: list[TVShowEpisodeTranslation] = session.exec(query.offset(offset).limit(limit if limit > 0 else None)).all() # type: ignore[arg-type]

        # Iterate the list to encase each item in the model requested
        response_model: list[TVShowEpisodeTranslationResponseItem] = [set_tv_show_episode_translation_response_model(tv_show_episode_translation, view) for tv_show_episode_translation in tv_show_episode_translation_list]

        return response_model

    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, tv_show_episode_id: int, language_code: str = None, view: TVShowEpisodeTranslationView = TVShowEpisodeTranslationView.BASIC) -> TVShowEpisodeTranslationResponseItem:
    """
    Retrieve a single TV show episode translation entry by its ID with optional detail level.

    Args:
        session (Session): SQLAlchemy session for database operations.
        tv_show_episode_id (int): The ID of the TV show episode translation entry to retrieve.
        language_code (str): The language code of the TV show episode translation entry to retrieve. If left None, all the translations with the same ID will be retrieved.
        view (TVShowEpisodeTranslationView): Determines the level of detail for the TV show episode translation entry.

    Returns:
        TVShowEpisodeTranslationResponseItem: The requested TV show episode translation entry serialized according to the specified view.

    Raises:
        ResourceNotFoundError: If the TV show episode translation entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Initialize the base query, filtering by id and language code, if necessary
        if not language_code:
            query: Select = select(TVShowEpisodeTranslation).where(TVShowEpisodeTranslation.episode_id == tv_show_episode_id)
        else:
            query: Select = select(TVShowEpisodeTranslation).where(
                and_(
                    TVShowEpisodeTranslation.media_id == tv_show_episode_id,
                    TVShowEpisodeTranslation.language_code == language_code
                )
            )

        # Set the level of detail requested
        query: Select = set_tv_show_episode_translation_detail_level(query, view)

        # Retrieve the media with the configuration set in the previous steps
        # If it doesn't exist, it will throw an error
        tv_show_episode_translation_db: TVShowEpisodeTranslation | None = session.exec(query).first()
        if not tv_show_episode_translation_db:
            if not language_code:
                raise ResourceNotFoundError(f"TVShowEpisodeTranslation with ID {tv_show_episode_id} not found")
            else:
                raise ResourceNotFoundError(f"TVShowEpisodeTranslation with ID {tv_show_episode_id} and language code {language_code} not found")

        # Encase the item in the requested model
        response_model = set_tv_show_episode_translation_response_model(tv_show_episode_translation_db, view)

        return response_model
    except ResourceNotFoundError as e:
        raise ResourceNotFoundError(e)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_tv_show_episode_translation: TVShowEpisodeTranslationCreate) -> TVShowEpisodeTranslationPublic:
    """
    Create a new TV show episode translation entry in the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        new_tv_show_episode_translation (TVShowEpisodeTranslationCreate): Input data for creating a new TV show episode translation entry.

    Returns:
        TVShowEpisodeTranslationPublic: The newly created TV show episode translation entry serialized for public exposure.

    Raises:
        RuntimeError: If a database or unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Create the new database record
        tv_show_episode_translation: TVShowEpisodeTranslation = TVShowEpisodeTranslation(**new_tv_show_episode_translation.model_dump())

        # Add the record to the session
        session.add(tv_show_episode_translation)

        # Commit the changes, storing the new record in the database
        session.commit()

        # Refresh the record model to get the whole record with the id generated by the database
        session.refresh(tv_show_episode_translation)
        return TVShowEpisodeTranslationPublic.model_validate(tv_show_episode_translation)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def update(session: Session, tv_show_episode_translation_id: int, language_code: str, tv_show_episode_translation_in: TVShowEpisodeTranslationUpdate) -> TVShowEpisodeTranslationPublic:
    """
    Update an existing TV show episode translation entry.

    Args:
        session (Session): SQLAlchemy session for database operations.
        tv_show_episode_translation_id (int): The ID of the TV show episode translation entry to update.
        language_code (str): The language code of the TV show episode translation entry to update.
        tv_show_episode_translation_in (TVShowEpisodeTranslationUpdate): Partial data for updating the TV show episode translation entry.

    Returns:
        TVShowEpisodeTranslation: The updated TV show episode translation entry serialized for public exposure.

    Raises:
        ResourceNotFoundError: If the TV show episode translation entry is not found.
        RuntimeError: If a database/unexpected error occurs.
        ValueError: If a data validation error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        tv_show_episode_translation_db: TVShowEpisodeTranslation = session.get(TVShowEpisodeTranslation, (tv_show_episode_translation_id, language_code))  # type: ignore[arg-type]
        if not tv_show_episode_translation_db:
            raise ResourceNotFoundError(f"TVShowEpisodeTranslation with ID {tv_show_episode_translation_id} and language code {language_code} not found")

        # Retrieve the input data to update the necessary fields
        tv_show_episode_translation_data: dict[str, Any] = tv_show_episode_translation_in.model_dump(exclude_unset=True)

        # Update the record with the new data
        media_db.sqlmodel_update(tv_show_episode_translation_data) # type: ignore[arg-type]

        # Save the changes to the database
        session.commit()

        # Retrieve the updated record from the database
        session.refresh(tv_show_episode_translation_db)

        return TVShowEpisodeTranslationPublic.model_validate(tv_show_episode_translation_db)
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

def delete(session: Session, tv_show_episode_translation_id: int, language_code: str) -> None:
    """
    Delete a TV show episode translation entry from the database.

    Args:
        session (Session): SQLAlchemy session for database operations.
        tv_show_episode_translation_id (int): The ID of the TV show episode translation entry to delete.
        language_code (str): The language code of the TV show episode translation entry to delete.

    Raises:
        ResourceNotFoundError: If the TV show episode translation entry is not found.
        RuntimeError: If a database/unexpected error occurs.
    """

    try:
        # Retrieve the record to update from the database
        # If it does not exist, it will throw an error
        tv_show_episode_translation: TVShowEpisodeTranslation = session.get(TVShowEpisodeTranslation, (tv_show_episode_translation_id, language_code)) # type: ignore[arg-type]
        if not tv_show_episode_translation:
            raise ResourceNotFoundError(f"TVShowEpisodeTranslation with ID {tv_show_episode_translation_id} and language code {language_code} not found")

        # Delete the record
        session.delete(tv_show_episode_translation)

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

def set_tv_show_episode_translation_detail_level(query: Select, view: TVShowEpisodeTranslationView) -> Select:
    """
    Add SQLAlchemy relationship loading options to a query based on the requested detail level.

    Args:
        query (Select): The SQLAlchemy Select query to modify.
        view (TVShowEpisodeTranslationView): The desired detail level for TV show episode translation entries.

    Returns:
        Select: The updated query with the appropriate loading options applied.
    """

    options_list: list[LoaderOption] = []

    if view == TVShowEpisodeTranslationView.WITH_EPISODE:
        options_list.append(selectinload(TVShowEpisodeTranslation.episode)) # type: ignore[arg-type]

    return query.options(*options_list) if options_list else query

def set_tv_show_episode_translation_response_model(tv_show_episode_translation: TVShowEpisodeTranslation, view: TVShowEpisodeTranslationView) -> TVShowEpisodeTranslationPublic | TVShowEpisodeTranslationPublicWithEpisode:
    """
    Serialize a single TVShowEpisodeTranslation instance into the appropriate response model based on the requested view.

    Args:
        tv_show_episode_translation (TVShowEpisodeTranslation): The TVShowEpisodeTranslation instance to serialize.
        view (TVShowEpisodeTranslationView): The desired view for serialization.

    Returns:
        TVShowEpisodeTranslationPublic: The serialized TV show episode translation instance according to the specified view.

    Raises:
        ValueError: If an invalid view type is provided.
    """
    match view:
        case TVShowEpisodeTranslationView.BASIC:
            return TVShowEpisodeTranslationPublic.model_validate(tv_show_episode_translation)
        case TVShowEpisodeTranslationView.WITH_EPISODE:
            return TVShowEpisodeTranslationPublicWithEpisode.model_validate(tv_show_episode_translation)
        case _:
            raise ValueError(f"Invalid view type: {view}")