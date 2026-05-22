from src.config.logging import configure_logging
from src.config.settings import load_settings
from src.scheduler.cron import start_scheduler
from src.storage.database import get_postgres_connection, init_postgres_db
from src.storage.repository import NewsRepository



def main() -> None:
    configure_logging()
    settings = load_settings()

    postgres_conn = get_postgres_connection(settings)
    init_postgres_db(postgres_conn)
    repository = NewsRepository(postgres_conn)

    start_scheduler(settings=settings, repository=repository)


if __name__ == "__main__":
    main()
