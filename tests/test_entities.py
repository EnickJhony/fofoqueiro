from datetime import datetime, timezone

from src.domain.entities import NewsItem


def test_news_item_stores_normalized_news_fields() -> None:
    published_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

    item = NewsItem(
        source_name="Portal X",
        source_url="https://example.com/feed",
        title="Noticia",
        link="https://example.com/noticia",
        published_at=published_at,
    )

    assert item.source_name == "Portal X"
    assert item.source_url == "https://example.com/feed"
    assert item.title == "Noticia"
    assert item.link == "https://example.com/noticia"
    assert item.published_at is published_at
