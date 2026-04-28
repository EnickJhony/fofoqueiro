from types import SimpleNamespace

import feedparser

from src.feeds.parser import parse_feed
from src.utils.datetime_utils import parse_rss_datetime


def test_parse_rss_datetime_converts_to_local_timezone() -> None:
    published_at = parse_rss_datetime("Mon, 01 Jan 2024 12:00:00 +0000", timezone_name="America/Manaus")

    assert published_at.isoformat() == "2024-01-01T08:00:00-04:00"


def test_parse_feed_converts_published_at_to_local_timezone(monkeypatch) -> None:
    fake_feed = SimpleNamespace(
        bozo=False,
        feed=SimpleNamespace(title="Portal X"),
        entries=[
            SimpleNamespace(
                title="Noticia 1",
                link="https://example.com/noticia-1",
                published="Mon, 01 Jan 2024 12:00:00 +0000",
            )
        ],
    )

    monkeypatch.setattr(feedparser, "parse", lambda source_url: fake_feed)

    news_items = parse_feed("https://example.com/feed", max_items=5, timezone_name="America/Manaus")

    assert len(news_items) == 1
    assert news_items[0].published_at.isoformat() == "2024-01-01T08:00:00-04:00"
