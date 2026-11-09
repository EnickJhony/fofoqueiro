from datetime import datetime, timezone

import pytest

from src.config.settings import Settings
from src.domain.entities import NewsItem
from src.scheduler import jobs


def _build_settings(send_to: str = "telegram") -> Settings:
    return Settings(
        postgres_dsn="",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_user="user",
        postgres_password="pass",
        postgres_db="database",
        postgres_sslmode="prefer",
        rss_sources=["https://example.com/feed"],
        fetch_interval_minutes=0,
        fetch_interval_hours=4,
        max_news_per_source=5,
        timezone_name="America/Manaus",
        send_to=send_to,
        telegram_bot_token="token",
        telegram_chat_ids=["chat"],
        whatsapp_phone="phone",
        whatsapp_apikey="apikey",
    )


def _news_item() -> NewsItem:
    return NewsItem(
        source_name="Portal X",
        source_url="https://example.com/feed",
        title="Noticia",
        link="https://example.com/noticia",
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


class FakeRepository:
    def __init__(self, rows: list[dict] | None = None) -> None:
        self.rows = rows or []
        self.saved_items: list[NewsItem] = []
        self.hours_requested: list[int] = []

    def save_news_items(self, news_items: list[NewsItem]) -> int:
        self.saved_items = news_items
        return len(news_items)

    def get_news_last_hours(self, hours: int) -> list[dict]:
        self.hours_requested.append(hours)
        return self.rows


def test_collect_and_store_job_collects_and_saves_news(monkeypatch, caplog) -> None:
    settings = _build_settings()
    repository = FakeRepository()
    collected = [_news_item()]
    collect_calls: list[tuple[list[str], int, str]] = []

    def fake_collect_news(source_urls, max_items_per_source, timezone_name):
        collect_calls.append((source_urls, max_items_per_source, timezone_name))
        return collected

    monkeypatch.setattr(jobs, "collect_news", fake_collect_news)

    with caplog.at_level("INFO"):
        jobs.collect_and_store_job(settings, repository)

    assert collect_calls == [
        (settings.rss_sources, settings.max_news_per_source, settings.timezone_name)
    ]
    assert repository.saved_items == collected
    assert "total_lido=1" in caplog.text
    assert "novos=1" in caplog.text


def test_send_daily_summary_job_queries_last_day_and_dispatches(monkeypatch) -> None:
    settings = _build_settings()
    rows = [{"source_name": "Portal X", "title": "Noticia", "link": "url"}]
    repository = FakeRepository(rows=rows)
    dispatched: list[tuple[Settings, str]] = []

    class FixedDateTime:
        @classmethod
        def now(cls, tz):
            return datetime(2026, 11, 8, 12, 0, tzinfo=tz)

    monkeypatch.setattr(jobs, "datetime", FixedDateTime)
    monkeypatch.setattr(
        jobs,
        "dispatch_message",
        lambda settings, message: dispatched.append((settings, message)) or True,
    )

    jobs.send_daily_summary_job(settings, repository)

    assert repository.hours_requested == [24]
    assert dispatched == [
        (
            settings,
            "Resumo do dia 2026-11-08\n\nPortal: Portal X\n- Noticia\n  url",
        )
    ]


def test_send_daily_summary_job_does_not_dispatch_when_channel_is_disabled(
    monkeypatch,
) -> None:
    settings = _build_settings(send_to="nenhum")
    repository = FakeRepository()
    dispatched: list[str] = []

    class FixedDateTime:
        @classmethod
        def now(cls, tz):
            return datetime(2026, 11, 8, 12, 0, tzinfo=tz)

    monkeypatch.setattr(jobs, "datetime", FixedDateTime)
    monkeypatch.setattr(
        jobs,
        "dispatch_message",
        lambda settings, message: dispatched.append(message) or False,
    )

    jobs.send_daily_summary_job(settings, repository)

    assert dispatched == [f"Resumo do dia 2026-11-08: sem noticias coletadas."]


def test_send_daily_summary_job_rejects_unknown_timezone(monkeypatch) -> None:
    settings = _build_settings()
    settings.timezone_name = "Unknown/Timezone"

    with pytest.raises(RuntimeError, match="Timezone invalida"):
        jobs.send_daily_summary_job(settings, FakeRepository())
