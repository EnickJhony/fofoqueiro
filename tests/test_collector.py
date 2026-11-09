from datetime import datetime, timezone

from src.domain.entities import NewsItem
from src.feeds import collector


def test_collect_news_combines_items_from_all_sources(monkeypatch) -> None:
    first_item = NewsItem(
        source_name="Portal A",
        source_url="https://a.example/feed",
        title="Noticia A",
        link="https://a.example/news",
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    second_item = NewsItem(
        source_name="Portal B",
        source_url="https://b.example/feed",
        title="Noticia B",
        link="https://b.example/news",
        published_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
    )
    calls: list[tuple[str, int, str]] = []

    def fake_parse_feed(source_url: str, max_items: int, timezone_name: str):
        calls.append((source_url, max_items, timezone_name))
        return [first_item] if source_url.startswith("https://a") else [second_item]

    monkeypatch.setattr(collector, "parse_feed", fake_parse_feed)

    result = collector.collect_news(
        source_urls=["https://a.example/feed", "https://b.example/feed"],
        max_items_per_source=3,
        timezone_name="America/Manaus",
    )

    assert result == [first_item, second_item]
    assert calls == [
        ("https://a.example/feed", 3, "America/Manaus"),
        ("https://b.example/feed", 3, "America/Manaus"),
    ]


def test_collect_news_continues_after_one_source_fails(monkeypatch, caplog) -> None:
    first_item = NewsItem(
        source_name="Portal A",
        source_url="https://a.example/feed",
        title="Noticia A",
        link="https://a.example/news",
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    third_item = NewsItem(
        source_name="Portal C",
        source_url="https://c.example/feed",
        title="Noticia C",
        link="https://c.example/news",
        published_at=datetime(2024, 1, 3, tzinfo=timezone.utc),
    )

    def fake_parse_feed(source_url: str, max_items: int, timezone_name: str):
        del max_items, timezone_name
        if source_url == "https://bad.example/feed":
            raise RuntimeError("feed indisponivel")
        return [first_item] if source_url.startswith("https://a") else [third_item]

    monkeypatch.setattr(collector, "parse_feed", fake_parse_feed)

    with caplog.at_level("ERROR"):
        result = collector.collect_news(
            [
                "https://a.example/feed",
                "https://bad.example/feed",
                "https://c.example/feed",
            ],
            max_items_per_source=5,
        )

    assert result == [first_item, third_item]
    assert "https://bad.example/feed" in caplog.text
