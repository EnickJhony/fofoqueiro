import logging

from src.domain.entities import NewsItem
from src.feeds.parser import parse_feed

logger = logging.getLogger(__name__)



def collect_news(
    source_urls: list[str],
    max_items_per_source: int,
    timezone_name: str = "America/Manaus",
) -> list[NewsItem]:
    all_news: list[NewsItem] = []

    for source_url in source_urls:
        try:
            all_news.extend(
                parse_feed(
                    source_url=source_url,
                    max_items=max_items_per_source,
                    timezone_name=timezone_name,
                )
            )
        except Exception:
            logger.exception("Falha ao coletar noticias da fonte: %s", source_url)

    return all_news
