import pytest

from src.config.settings import Settings
from src.scheduler import cron


def _build_settings(minutes: int, hours: int) -> Settings:
    return Settings(
        postgres_dsn="",
        postgres_host="localhost",
        postgres_port=5432,
        postgres_user="user",
        postgres_password="pass",
        postgres_db="database",
        postgres_sslmode="prefer",
        rss_sources=[],
        fetch_interval_minutes=minutes,
        fetch_interval_hours=hours,
        max_news_per_source=5,
        timezone_name="America/Manaus",
        send_to="nenhum",
        telegram_bot_token="",
        telegram_chat_ids=[],
        whatsapp_phone="",
        whatsapp_apikey="",
    )


class StopScheduler(Exception):
    pass


class FakeScheduleJob:
    def __init__(self, interval: int | None) -> None:
        self.interval = interval
        self.unit: str | None = None
        self.at_time: str | None = None
        self.callback = None
        self.kwargs = None

    @property
    def minutes(self):
        self.unit = "minutes"
        return self

    @property
    def hours(self):
        self.unit = "hours"
        return self

    @property
    def day(self):
        self.unit = "days"
        return self

    def do(self, callback, **kwargs):
        self.callback = callback
        self.kwargs = kwargs
        return self

    def at(self, at_time: str):
        self.at_time = at_time
        return self


class FakeSchedule:
    def __init__(self) -> None:
        self.jobs: list[FakeScheduleJob] = []

    def every(self, interval: int | None = None) -> FakeScheduleJob:
        job = FakeScheduleJob(interval)
        self.jobs.append(job)
        return job

    def run_pending(self) -> None:
        raise StopScheduler


@pytest.mark.parametrize(
    ("minutes", "hours", "expected_interval", "expected_unit"),
    [(10, 4, 10, "minutes"), (0, 4, 4, "hours")],
)
def test_start_scheduler_registers_collection_and_summary_jobs(
    monkeypatch,
    minutes,
    hours,
    expected_interval,
    expected_unit,
) -> None:
    fake_schedule = FakeSchedule()
    monkeypatch.setattr(cron, "schedule", fake_schedule)
    monkeypatch.setattr(cron.time, "sleep", lambda seconds: None)

    settings = _build_settings(minutes, hours)

    with pytest.raises(StopScheduler):
        cron.start_scheduler(settings, object())

    collection_job, summary_job = fake_schedule.jobs
    assert collection_job.interval == expected_interval
    assert collection_job.unit == expected_unit
    assert collection_job.callback is cron.collect_and_store_job
    assert summary_job.at_time == "18:00"
    assert summary_job.callback is cron.send_daily_summary_job
