import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import psycopg
import pytest
from dotenv import load_dotenv
from psycopg.rows import dict_row

from src.domain.entities import NewsItem
from src.storage.database import init_postgres_db
from src.storage.repository import NewsRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def postgres_connection():
    load_dotenv()
    dsn = os.getenv("TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("TEST_POSTGRES_DSN is not configured")
    if urlparse(dsn).path.lstrip("/") != "fofoqueiro_test":
        pytest.fail("TEST_POSTGRES_DSN must point to fofoqueiro_test")

    connection = psycopg.connect(dsn, row_factory=dict_row)
    connection.autocommit = False
    init_postgres_db(connection)

    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE news RESTART IDENTITY")
    connection.commit()

    try:
        yield connection
    finally:
        connection.close()


def _item(link: str, published_at: datetime) -> NewsItem:
    return NewsItem(
        source_name="Portal X",
        source_url="https://example.com/feed",
        title=f"Noticia {link.rsplit('/', maxsplit=1)[-1]}",
        link=link,
        published_at=published_at,
    )


def test_repository_inserts_and_deduplicates_by_link(postgres_connection) -> None:
    repository = NewsRepository(postgres_connection)
    published_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    item = _item("https://example.com/news-1", published_at)

    inserted_first = repository.save_news_items([item])
    inserted_second = repository.save_news_items([item])

    assert inserted_first == 1
    assert inserted_second == 0
    assert len(repository.get_news_for_day(published_at.date())) == 1


def test_repository_queries_news_for_day(postgres_connection) -> None:
    repository = NewsRepository(postgres_connection)
    target_date = datetime(2024, 1, 2, tzinfo=timezone.utc)
    repository.save_news_items(
        [
            _item("https://example.com/target", target_date),
            _item("https://example.com/other", target_date - timedelta(days=1)),
        ]
    )

    rows = repository.get_news_for_day(target_date.date())

    assert [row["link"] for row in rows] == ["https://example.com/target"]


def test_repository_queries_news_from_last_hours(postgres_connection) -> None:
    repository = NewsRepository(postgres_connection)
    now = datetime.now(timezone.utc)
    repository.save_news_items(
        [
            _item("https://example.com/recent", now - timedelta(hours=1)),
            _item("https://example.com/old", now - timedelta(hours=25)),
        ]
    )

    rows = repository.get_news_last_hours(24)

    assert [row["link"] for row in rows] == ["https://example.com/recent"]
