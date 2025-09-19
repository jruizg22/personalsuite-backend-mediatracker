from pydantic import ValidationError
from typing import Sequence
from sqlalchemy.exc import OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError
from sqlmodel import Session, select

from media_tracker.models.yt import YTChannel, YTChannelPublic


def get_all(session: Session, offset: int = 0, limit: int = 100) -> list[YTChannelPublic]:
    try:
        yt_channel_db: Sequence[YTChannel] = session.exec(select(YTChannel).offset(offset).limit(limit)).all()
        return [YTChannelPublic.model_validate(yt_channel) for yt_channel in yt_channel_db]
    except (OperationalError, StatementError, SQLAlchemyError, TimeoutError, DBAPIError) as e:
        raise RuntimeError(f"Database error: {e}") from e
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Data validation error: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}") from e