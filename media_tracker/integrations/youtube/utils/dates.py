from datetime import datetime


def parse_ytdlp_datetime(date_str: str | None) -> datetime | None:
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y%m%d")

    except ValueError:
        return None