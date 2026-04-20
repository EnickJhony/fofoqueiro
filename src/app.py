from src.config.logging import configure_logging
from src.config.settings import load_settings
from src.scheduler.cron import start_scheduler
from src.storage.database import get_connection, get_postgres_connection, init_db, init_postgres_db
from src.storage.repository import MultiNewsRepository, NewsRepository, PostgresNewsRepository



def main() -> None:
    configure_logging()
    settings = load_settings()

    sqlite_repository = None
    if settings.sqlite_enabled:
        sqlite_conn = get_connection(settings.db_path)
        init_db(sqlite_conn)
        sqlite_repository = NewsRepository(sqlite_conn)

    postgres_repository = None
    if settings.postgres_enabled:
        postgres_conn = get_postgres_connection(settings)
        init_postgres_db(postgres_conn)
        postgres_repository = PostgresNewsRepository(postgres_conn)

    if sqlite_repository and postgres_repository:
        repository = MultiNewsRepository(primary=sqlite_repository, secondaries=[postgres_repository])
    elif sqlite_repository:
        repository = sqlite_repository
    elif postgres_repository:
        repository = postgres_repository
    else:
        raise RuntimeError(
            "Nenhum banco habilitado. Defina SQLITE_ENABLED=true ou POSTGRES_ENABLED=true."
        )

    start_scheduler(settings=settings, repository=repository)


if __name__ == "__main__":
    main()
