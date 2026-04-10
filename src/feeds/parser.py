import logging

import feedparser

from src.domain.entities import NewsItem
from src.utils.datetime_utils import parse_rss_datetime

logger = logging.getLogger(__name__)



def parse_feed(source_url: str, max_items: int) -> list[NewsItem]:
    parsed = feedparser.parse(source_url)

    if parsed.bozo:
        logger.warning("Falha ao ler feed: %s", source_url)
        return []

    source_name = getattr(parsed.feed, "title", source_url)
    output: list[NewsItem] = []

    for entry in parsed.entries[:max_items]:
        title = getattr(entry, "title", "Sem titulo")
        link = getattr(entry, "link", "")
        published_raw = getattr(entry, "published", "")

        if not link:
            continue

        output.append(
            NewsItem(
                source_name=source_name,
                source_url=source_url,
                title=title,
                link=link,
                published_at=parse_rss_datetime(published_raw),
            )
        )

    return output
