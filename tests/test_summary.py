from datetime import date

from src.summarizer.daily_summary import build_daily_summary


def test_build_daily_summary_groups_news_by_source() -> None:
    rows = [
        {"source_name": "Portal A", "title": "Primeira", "link": "https://a/1"},
        {"source_name": "Portal A", "title": "Segunda", "link": "https://a/2"},
        {"source_name": "Portal B", "title": "Terceira", "link": "https://b/1"},
    ]

    summary = build_daily_summary(rows, date(2024, 1, 1))

    assert summary == (
        "Resumo do dia 2024-01-01\n\n"
        "Portal: Portal A\n"
        "- Primeira\n  https://a/1\n"
        "- Segunda\n  https://a/2\n\n"
        "Portal: Portal B\n"
        "- Terceira\n  https://b/1"
    )


def test_build_daily_summary_reports_empty_day() -> None:
    assert build_daily_summary([], date(2024, 1, 1)) == (
        "Resumo do dia 2024-01-01: sem noticias coletadas."
    )
