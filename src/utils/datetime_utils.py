from datetime import datetime, timezone
from email.utils import parsedate_to_datetime



def parse_rss_datetime(raw_value: str) -> datetime:
    if not raw_value:
        return datetime.now(tz=timezone.utc)

    try:
        dt = parsedate_to_datetime(raw_value)
    except Exception:
        return datetime.now(tz=timezone.utc)

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt
