from src.domain.entities import NewsItem
from src.feeds.parser import parse_feed



def collect_news(source_urls: list[str], max_items_per_source: int) -> list[NewsItem]:
    all_news: list[NewsItem] = []

    for source_url in source_urls:
        all_news.extend(parse_feed(source_url=source_url, max_items=max_items_per_source))

    return all_news
