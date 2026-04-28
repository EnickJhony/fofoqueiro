from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError



def parse_rss_datetime(raw_value: str, timezone_name: str = "America/Manaus") -> datetime:
    if not raw_value:
        return datetime.now(tz=timezone.utc)

    try:
        dt = parsedate_to_datetime(raw_value)
    except Exception:
        return datetime.now(tz=timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    try:
        local_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        local_timezone = timezone.utc

    return dt.astimezone(local_timezone)
