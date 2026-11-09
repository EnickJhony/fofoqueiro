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


def test_parse_feed_ignores_entries_without_links(monkeypatch) -> None:
    fake_feed = SimpleNamespace(
        bozo=False,
        feed=SimpleNamespace(title="Portal X"),
        entries=[
            SimpleNamespace(title="Sem link", link="", published="Mon, 01 Jan 2024 12:00:00 +0000"),
            SimpleNamespace(
                title="Com link",
                link="https://example.com/noticia",
                published="Mon, 01 Jan 2024 12:00:00 +0000",
            ),
        ],
    )
    monkeypatch.setattr(feedparser, "parse", lambda source_url: fake_feed)

    news_items = parse_feed("https://example.com/feed", max_items=5)

    assert len(news_items) == 1
    assert news_items[0].title == "Com link"


def test_parse_feed_returns_empty_list_for_invalid_feed(monkeypatch) -> None:
    fake_feed = SimpleNamespace(bozo=True, entries=[])
    monkeypatch.setattr(feedparser, "parse", lambda source_url: fake_feed)

    assert parse_feed("https://example.com/feed", max_items=5) == []


def test_parse_feed_uses_source_url_when_feed_has_no_title(monkeypatch) -> None:
    fake_feed = SimpleNamespace(
        bozo=False,
        feed=SimpleNamespace(),
        entries=[
            SimpleNamespace(
                title="Noticia",
                link="https://example.com/noticia",
                published="Mon, 01 Jan 2024 12:00:00 +0000",
            )
        ],
    )
    monkeypatch.setattr(feedparser, "parse", lambda source_url: fake_feed)

    news_items = parse_feed("https://example.com/feed", max_items=5)

    assert news_items[0].source_name == "https://example.com/feed"


def test_parse_feed_uses_utc_for_entry_without_date(monkeypatch) -> None:
    fake_feed = SimpleNamespace(
        bozo=False,
        feed=SimpleNamespace(title="Portal X"),
        entries=[
            SimpleNamespace(
                title="Noticia",
                link="https://example.com/noticia",
            )
        ],
    )
    monkeypatch.setattr(feedparser, "parse", lambda source_url: fake_feed)

    news_items = parse_feed("https://example.com/feed", max_items=5)

    assert news_items[0].published_at.tzinfo is not None
