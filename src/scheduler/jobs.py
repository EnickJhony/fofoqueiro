import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.config.settings import Settings
from src.feeds.collector import collect_news
from src.feeds.sources import get_feed_sources
from src.notifiers.dispatcher import dispatch_message
from src.storage.repository import NewsRepository
from src.summarizer.daily_summary import build_daily_summary

logger = logging.getLogger(__name__)



def collect_and_store_job(settings: Settings, repository: NewsRepository) -> None:
    source_urls = get_feed_sources(settings)
    all_news = collect_news(
        source_urls=source_urls,
        max_items_per_source=settings.max_news_per_source,
    )
    inserted = repository.save_news_items(all_news)

    logger.info(
        "Coleta finalizada | fontes=%s | total_lido=%s | novos=%s",
        len(source_urls),
        len(all_news),
        inserted,
    )



def send_daily_summary_job(settings: Settings, repository: NewsRepository) -> None:
    tz = ZoneInfo(settings.timezone_name)
    today = datetime.now(tz=tz).date()
    rows = repository.get_news_for_day(today)
    summary = build_daily_summary(rows, today)
    sent = dispatch_message(settings=settings, message=summary)

    if settings.send_to in {"telegram", "whatsapp", "ambos"}:
        if sent:
            logger.info("Resumo diario enviado | data=%s | itens=%s", today.isoformat(), len(rows))
        else:
            logger.warning(
                "Resumo diario gerado mas houve falha no envio | data=%s | itens=%s | canal=%s",
                today.isoformat(),
                len(rows),
                settings.send_to,
            )
    else:
        logger.info(
            "Resumo diario gerado sem envio | data=%s | itens=%s | canal=%s",
            today.isoformat(),
            len(rows),
            settings.send_to,
        )
