from datetime import timezone

from src.utils.datetime_utils import parse_rss_datetime


def test_parse_rss_datetime_uses_utc_for_invalid_input() -> None:
    parsed = parse_rss_datetime("not a date")

    assert parsed.tzinfo == timezone.utc


def test_parse_rss_datetime_uses_utc_for_missing_input() -> None:
    parsed = parse_rss_datetime("")

    assert parsed.tzinfo == timezone.utc


def test_parse_rss_datetime_falls_back_to_utc_for_unknown_timezone() -> None:
    parsed = parse_rss_datetime(
        "Mon, 01 Jan 2024 12:00:00 +0000",
        timezone_name="Unknown/Timezone",
    )

    assert parsed.isoformat() == "2024-01-01T12:00:00+00:00"
