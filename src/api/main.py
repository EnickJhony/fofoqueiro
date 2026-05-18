from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import api_router
from src.config.settings import load_settings
from src.storage.database import (
    get_connection,
    init_db,
    get_postgres_connection,
    init_postgres_db,
)
from src.storage.repository import (
    NewsRepository,
    PostgresNewsRepository,
    MultiNewsRepository,
)


app = FastAPI(title="Fofoqueiro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def startup_event() -> None:
    settings = load_settings()

    sqlite_repository = None
    if settings.sqlite_enabled:
        sqlite_conn = get_connection(settings.db_path)
        init_db(sqlite_conn)
        sqlite_repository = NewsRepository(sqlite_conn)

    postgres_repository = None
    if settings.postgres_enabled:
        pg_conn = get_postgres_connection(settings)
        init_postgres_db(pg_conn)
        postgres_repository = PostgresNewsRepository(pg_conn)

    if sqlite_repository and postgres_repository:
        repository = MultiNewsRepository(primary=sqlite_repository, secondaries=[postgres_repository])
    elif sqlite_repository:
        repository = sqlite_repository
    elif postgres_repository:
        repository = postgres_repository
    else:
        raise RuntimeError("Nenhum banco habilitado. Defina SQLITE_ENABLED=true ou POSTGRES_ENABLED=true.")

    app.state.settings = settings
    app.state.repository = repository
