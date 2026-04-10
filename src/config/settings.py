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



def load_settings() -> Settings:
    load_dotenv(dotenv_path=Path(".env"), override=False)

    rss_from_env = _split_csv(os.getenv("RSS_SOURCES", ""))

    return Settings(
        db_path=os.getenv("DB_PATH", "data/fofoqueiro.db"),
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
