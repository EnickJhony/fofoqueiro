from src.config.logging import configure_logging
from src.config.settings import load_settings
from src.scheduler.cron import start_scheduler
from src.storage.database import get_connection, init_db
from src.storage.repository import NewsRepository



def main() -> None:
    configure_logging()
    settings = load_settings()

    conn = get_connection(settings.db_path)
    init_db(conn)

    repository = NewsRepository(conn)
    start_scheduler(settings=settings, repository=repository)


if __name__ == "__main__":
    main()
