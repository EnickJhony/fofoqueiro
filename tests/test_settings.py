from src.config import settings as settings_module


def _clear_settings_environment(monkeypatch) -> None:
    for name in (
        "DATABASE_URL",
        "DATABASE_PUBLIC_URL",
        "POSTGRES_DSN",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_SSLMODE",
        "RSS_SOURCES",
        "FETCH_INTERVAL_MINUTES",
        "FETCH_INTERVAL_HOURS",
        "MAX_NOTICIAS",
        "TIMEZONE_NAME",
        "ENVIAR_PARA",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_IDS",
        "WHATSAPP_PHONE",
        "WHATSAPP_APIKEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_load_settings_uses_defaults(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)
    monkeypatch.setattr(settings_module, "load_dotenv", lambda **kwargs: False)

    settings = settings_module.load_settings()

    assert settings.rss_sources == settings_module.DEFAULT_RSS_SOURCES
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432
    assert settings.fetch_interval_hours == 4
    assert settings.fetch_interval_minutes == 0
    assert settings.max_news_per_source == 5
    assert settings.timezone_name == "America/Manaus"
    assert settings.send_to == "nenhum"


def test_load_settings_parses_custom_values(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)
    monkeypatch.setattr(settings_module, "load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv("RSS_SOURCES", " https://one.example/feed, https://two.example/feed ")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("FETCH_INTERVAL_MINUTES", "10")
    monkeypatch.setenv("MAX_NOTICIAS", "8")
    monkeypatch.setenv("ENVIAR_PARA", "telegram")
    monkeypatch.setenv("TELEGRAM_CHAT_IDS", "111, 222")

    settings = settings_module.load_settings()

    assert settings.rss_sources == [
        "https://one.example/feed",
        "https://two.example/feed",
    ]
    assert settings.postgres_port == 5433
    assert settings.fetch_interval_minutes == 10
    assert settings.max_news_per_source == 8
    assert settings.send_to == "telegram"
    assert settings.telegram_chat_ids == ["111", "222"]


def test_load_settings_prioritizes_database_url(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)
    monkeypatch.setattr(settings_module, "load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://database-url")
    monkeypatch.setenv("DATABASE_PUBLIC_URL", "postgresql://public-url")
    monkeypatch.setenv("POSTGRES_DSN", "postgresql://postgres-dsn")

    settings = settings_module.load_settings()

    assert settings.postgres_dsn == "postgresql://database-url"
