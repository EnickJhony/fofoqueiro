from datetime import datetime, timezone

from src.domain.entities import NewsItem
from src.storage.repository import NewsRepository


class FakeCursor:
    def __init__(self, rowcounts: list[int], rows: list[dict] | None = None) -> None:
        self.rowcounts = iter(rowcounts)
        self.rows = rows or []
        self.executed: list[tuple[str, tuple]] = []
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query: str, params: tuple) -> None:
        self.executed.append((query, params))
        self.rowcount = next(self.rowcounts)

    def fetchall(self) -> list[dict]:
        return self.rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.cursor_instance = cursor
        self.commits = 0

    def cursor(self) -> FakeCursor:
        return self.cursor_instance

    def commit(self) -> None:
        self.commits += 1


def _news_item() -> NewsItem:
    return NewsItem(
        source_name="Portal X",
        source_url="https://example.com/feed",
        title="Noticia",
        link="https://example.com/noticia",
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def test_save_news_items_counts_only_inserted_rows() -> None:
    cursor = FakeCursor(rowcounts=[1, 0])
    connection = FakeConnection(cursor)
    repository = NewsRepository(connection)

    inserted = repository.save_news_items([_news_item(), _news_item()])

    assert inserted == 1
    assert connection.commits == 1
    assert len(cursor.executed) == 2


def test_get_news_for_day_returns_repository_rows() -> None:
    rows = [{"source_name": "Portal X", "title": "Noticia", "link": "url", "published_at": "date"}]
    cursor = FakeCursor(rowcounts=[0], rows=rows)
    connection = FakeConnection(cursor)
    repository = NewsRepository(connection)

    result = repository.get_news_for_day(datetime(2024, 1, 1).date())

    assert result == rows
    assert cursor.executed[0][1] == ("2024-01-01",)
