from src.config.logging import configure_logging
from src.config.settings import load_settings
from src.scheduler.cron import start_scheduler
from src.storage.database import get_postgres_connection, init_postgres_db
from src.storage.repository import NewsRepository



def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")

    if path in {"/", "/healthz"}:
        status = "200 OK"
        body = b"fofoqueiro running\n"
    else:
        status = "404 Not Found"
        body = b"not found\n"

    headers = [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]


application = app


def main() -> None:
    configure_logging()
    settings = load_settings()

    postgres_conn = get_postgres_connection(settings)
    init_postgres_db(postgres_conn)
    repository = NewsRepository(postgres_conn)

    start_scheduler(settings=settings, repository=repository)


if __name__ == "__main__":
    main()
