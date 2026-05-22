from datetime import date

from src.domain.entities import NewsItem


class NewsRepository:
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

    def get_news_last_hours(self, hours: int) -> list:
        query = """
            SELECT source_name, title, link, published_at
            FROM news
            WHERE published_at > NOW() - make_interval(hours => %s)
            ORDER BY source_name, published_at DESC
        """
        with self.conn.cursor() as cursor:
            cursor.execute(query, (hours,))
            rows = cursor.fetchall()
        return rows
