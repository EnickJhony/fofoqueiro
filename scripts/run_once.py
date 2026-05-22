from src.config.logging import configure_logging
from src.config.settings import load_settings
from src.scheduler.jobs import collect_and_store_job, send_daily_summary_job
from src.storage.database import get_postgres_connection, init_postgres_db
from src.storage.repository import NewsRepository



def main() -> None:
    configure_logging()
    settings = load_settings()

    postgres_conn = get_postgres_connection(settings)
    init_postgres_db(postgres_conn)
    repository = NewsRepository(postgres_conn)

    collect_and_store_job(settings=settings, repository=repository)
    send_daily_summary_job(settings=settings, repository=repository)


if __name__ == "__main__":
    main()
