import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_RSS_SOURCES = [
    "https://d24am.com/feed/",
    "https://www.portaldoholanda.com.br/feed/",
    "https://amazonasatual.com.br/feed/",
    "https://portalmanausalerta.com.br/feed/",
]


@dataclass(slots=True)
class Settings:
    db_path: str
    postgres_enabled: bool
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    rss_sources: list[str]
    fetch_interval_hours: int
    max_news_per_source: int
    timezone_name: str
    send_to: str
    telegram_bot_token: str
    telegram_chat_id: str
    whatsapp_phone: str
    whatsapp_apikey: str



def _split_csv(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on", "sim"}



def load_settings() -> Settings:
    load_dotenv(dotenv_path=Path(".env"), override=False)

    rss_from_env = _split_csv(os.getenv("RSS_SOURCES", ""))

    return Settings(
        db_path=os.getenv("DB_PATH", "data/fofoqueiro.db"),
        postgres_enabled=_as_bool(os.getenv("POSTGRES_ENABLED", "false")),
        postgres_host=os.getenv("POSTGRES_HOST", "localhost").strip(),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
        postgres_user=os.getenv("POSTGRES_USER", "fofoqueiro").strip(),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "").strip(),
        postgres_db=os.getenv("POSTGRES_DB", "fofoqueiro").strip(),
        rss_sources=rss_from_env or DEFAULT_RSS_SOURCES,
        fetch_interval_hours=int(os.getenv("FETCH_INTERVAL_HOURS", "4")),
        max_news_per_source=int(os.getenv("MAX_NOTICIAS", "5")),
        timezone_name=os.getenv("TIMEZONE_NAME", "America/Manaus"),
        send_to=os.getenv("ENVIAR_PARA", "nenhum").strip().lower(),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        whatsapp_phone=os.getenv("WHATSAPP_PHONE", "").strip(),
        whatsapp_apikey=os.getenv("WHATSAPP_APIKEY", "").strip(),
    )
