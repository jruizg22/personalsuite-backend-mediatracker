from pydantic import ValidationError
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlmodel import Session, select

from media_tracker.models.media import Media, MediaUpdate, MediaPublic, MediaCreate


def get_all(session: Session, offset: int = 0, limit: int = 100) -> list[MediaPublic]:
    try:
        media_db = session.exec(select(Media).offset(offset).limit(limit)).all()
        return [MediaPublic.model_validate(media) for media in media_db]
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def get_by_id(session: Session, media_id: int) -> MediaPublic:
    try:
        media_db = session.get(Media, media_id)
        if not media_db:
            raise RuntimeError(f"Media with ID {media_id} not found")
        return MediaPublic.model_validate(media_db)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e

def create(session: Session, new_media: MediaCreate) -> MediaPublic:
    try:
        media = Media(**new_media.model_dump())
        session.add(media)
        session.commit()
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
    try:
        media_db = session.get(Media, media_id)
        if not media_db:
            raise RuntimeError(f"Media with ID {media_id} not found")
        media_data = media_in.model_dump(exclude_unset=True)
        media_db.sqlmodel_update(media_data)
        session.commit()
        session.refresh(media_db)
        return MediaPublic.model_validate(media_db)
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        session.rollback()
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e

def delete(session: Session, media_id: int) -> dict:
    try:
        media = session.get(Media, media_id)
        if not media:
            raise RuntimeError(f"Media with ID {media_id} not found")
        session.delete(media)
        session.commit()
        return {"ok": True}
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        session.rollback()
        raise RuntimeError(f"Database error: {e}") from e
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"Unexpected error: {e}") from e