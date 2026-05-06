from datetime import date, datetime

from pydantic import field_validator


class DateNormalizationMixin:
    @staticmethod
    def _normalize_date(value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            if "T" in value:
                return datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                ).date()

            return date.fromisoformat(value)

        return value

    @field_validator(
        "created_at",
        "published_at",
        "updated_at",
        mode="before",
        check_fields=False
    )
    @classmethod
    def normalize_dates(cls, value):
        return cls._normalize_date(value)