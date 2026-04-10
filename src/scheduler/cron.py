import logging
import time

import schedule

from src.config.settings import Settings
from src.scheduler.jobs import collect_and_store_job, send_daily_summary_job
from src.storage.repository import NewsRepository

logger = logging.getLogger(__name__)



def start_scheduler(settings: Settings, repository: NewsRepository) -> None:
    schedule.every(settings.fetch_interval_hours).hours.do(
        collect_and_store_job,
        settings=settings,
        repository=repository,
    )

    summary_hour = 18
    summary_minute = 0
    schedule.every().day.at(f"{summary_hour:02d}:{summary_minute:02d}").do(
        send_daily_summary_job,
        settings=settings,
        repository=repository,
    )

    logger.info("Scheduler iniciado | coleta=%sh | resumo=18:00", settings.fetch_interval_hours)

    while True:
        schedule.run_pending()
        time.sleep(1)
