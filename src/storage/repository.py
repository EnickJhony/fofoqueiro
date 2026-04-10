import sqlite3
from datetime import date

from src.domain.entities import NewsItem



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
