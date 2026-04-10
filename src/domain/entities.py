from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class NewsItem:
    source_name: str
    source_url: str
    title: str
    link: str
    published_at: datetime
