import pytest

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


def test_load_settings_falls_back_to_default_sources_for_empty_value(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)
    monkeypatch.setattr(settings_module, "load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv("RSS_SOURCES", " , ")

    settings = settings_module.load_settings()

    assert settings.rss_sources == settings_module.DEFAULT_RSS_SOURCES


def test_load_settings_strips_text_values(monkeypatch) -> None:
    _clear_settings_environment(monkeypatch)
    monkeypatch.setattr(settings_module, "load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv("POSTGRES_HOST", " db.example ")
    monkeypatch.setenv("POSTGRES_USER", " app ")
    monkeypatch.setenv("POSTGRES_PASSWORD", " secret ")
    monkeypatch.setenv("POSTGRES_SSLMODE", " REQUIRE ")
    monkeypatch.setenv("ENVIAR_PARA", " TELEGRAM ")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", " token ")

    settings = settings_module.load_settings()

    assert settings.postgres_host == "db.example"
    assert settings.postgres_user == "app"
    assert settings.postgres_password == "secret"
    assert settings.postgres_sslmode == "require"
    assert settings.send_to == "telegram"
    assert settings.telegram_bot_token == "token"


@pytest.mark.parametrize(
    "variable_name",
    [
        "POSTGRES_PORT",
        "FETCH_INTERVAL_MINUTES",
        "FETCH_INTERVAL_HOURS",
        "MAX_NOTICIAS",
    ],
)
def test_load_settings_rejects_non_integer_values(monkeypatch, variable_name) -> None:
    _clear_settings_environment(monkeypatch)
    monkeypatch.setattr(settings_module, "load_dotenv", lambda **kwargs: False)
    monkeypatch.setenv(variable_name, "not-a-number")

    with pytest.raises(ValueError):
        settings_module.load_settings()
