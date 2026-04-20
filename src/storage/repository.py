import sqlite3
from datetime import date
from typing import Protocol

from src.domain.entities import NewsItem


class RepositoryLike(Protocol):
    def save_news_items(self, news_items: list[NewsItem]) -> int:
        ...

    def get_news_for_day(self, day: date) -> list:
        ...


class NewsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def save_news_items(self, news_items: list[NewsItem]) -> int:
        inserted = 0

        for item in news_items:
            cursor = self.conn.execute(
                """
                INSERT OR IGNORE INTO news (source_name, source_url, title, link, published_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    item.source_name,
                    item.source_url,
                    item.title,
                    item.link,
                    item.published_at.isoformat(),
                ),
            )
            if cursor.rowcount > 0:
                inserted += 1

        self.conn.commit()
        return inserted

    def get_news_for_day(self, day: date) -> list[sqlite3.Row]:
        day_str = day.isoformat()
        query = """
            SELECT source_name, title, link, published_at
            FROM news
            WHERE substr(published_at, 1, 10) = ?
            ORDER BY source_name, published_at DESC
        """
        rows = self.conn.execute(query, (day_str,)).fetchall()
        return rows


class PostgresNewsRepository:
    def __init__(self, conn) -> None:
        self.conn = conn

    def save_news_items(self, news_items: list[NewsItem]) -> int:
        inserted = 0

        with self.conn.cursor() as cursor:
            for item in news_items:
                cursor.execute(
                    """
                    INSERT INTO news (source_name, source_url, title, link, published_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (link) DO NOTHING
                    """,
                    (
                        item.source_name,
                        item.source_url,
                        item.title,
                        item.link,
                        item.published_at.isoformat(),
                    ),
                )
                if cursor.rowcount > 0:
                    inserted += 1

        self.conn.commit()
        return inserted

    def get_news_for_day(self, day: date) -> list:
        day_str = day.isoformat()
        query = """
            SELECT source_name, title, link, published_at
            FROM news
            WHERE substring(published_at from 1 for 10) = %s
            ORDER BY source_name, published_at DESC
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (day_str,))
            rows = cursor.fetchall()
        return rows


class MultiNewsRepository:
    def __init__(self, primary: RepositoryLike, secondaries: list[RepositoryLike] | None = None) -> None:
        self.primary = primary
        self.secondaries = secondaries or []

    def save_news_items(self, news_items: list[NewsItem]) -> int:
        inserted_primary = self.primary.save_news_items(news_items)

        for repository in self.secondaries:
            repository.save_news_items(news_items)

        return inserted_primary

    def get_news_for_day(self, day: date) -> list:
        return self.primary.get_news_for_day(day)
