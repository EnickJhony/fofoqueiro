from src.config.settings import Settings

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    published_at TEXT NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_postgres_connection(settings: Settings):
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise RuntimeError(
            "Dependencia do PostgreSQL ausente. Instale com: pip install psycopg[binary]"
        ) from exc

    if settings.postgres_dsn:
        conn = psycopg.connect(settings.postgres_dsn, row_factory=dict_row)
    else:
        conn = psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            dbname=settings.postgres_db,
            sslmode=settings.postgres_sslmode,
            row_factory=dict_row,
        )
    conn.autocommit = False
    return conn


def init_postgres_db(conn) -> None:
    with conn.cursor() as cursor:
        cursor.execute(POSTGRES_SCHEMA)
    conn.commit()
