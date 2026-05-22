from src.config.settings import Settings

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id BIGSERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    published_at TIMESTAMPTZ NOT NULL,
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
        cursor.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'news'
                      AND column_name = 'published_at'
                      AND data_type IN ('text', 'character varying', 'character')
                ) THEN
                    ALTER TABLE news
                        ALTER COLUMN published_at
                        TYPE TIMESTAMPTZ
                        USING published_at::timestamptz;
                END IF;
            END $$;
            """
        )
    conn.commit()
