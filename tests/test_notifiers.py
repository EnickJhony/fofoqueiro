from urllib.parse import parse_qs

from src.config.settings import Settings
from src.notifiers.dispatcher import dispatch_message
from src.notifiers.telegram import (
    MAX_TELEGRAM_MESSAGE_LENGTH,
    _normalize_chat_id,
    send_telegram_message,
)


def _build_settings(send_to: str) -> Settings:
    return Settings(
        db_path="data/fofoqueiro.db",
        rss_sources=[],
        fetch_interval_hours=4,
        max_news_per_source=5,
        timezone_name="America/Manaus",
        send_to=send_to,
        telegram_bot_token="token",
        telegram_chat_id="chat",
        whatsapp_phone="phone",
        whatsapp_apikey="apikey",
    )


def test_send_telegram_message_splits_large_payload(monkeypatch) -> None:
    payloads: list[str] = []

    class DummyResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(request, timeout=20):
        del timeout
        payloads.append(request.data.decode("utf-8"))
        return DummyResponse()

    monkeypatch.setattr("src.notifiers.telegram.urlopen", fake_urlopen)

    message = "a" * (MAX_TELEGRAM_MESSAGE_LENGTH + 50)
    success = send_telegram_message(token="token", chat_id="chat", message=message)

    assert success is True
    assert len(payloads) == 2

    rebuilt_message = ""
    for payload in payloads:
        rebuilt_message += parse_qs(payload)["text"][0]

    assert rebuilt_message == message


def test_dispatch_message_returns_false_when_disabled() -> None:
    settings = _build_settings(send_to="nenhum")
    assert dispatch_message(settings, "mensagem") is False


def test_dispatch_message_ambos_requires_both(monkeypatch) -> None:
    settings = _build_settings(send_to="ambos")

    monkeypatch.setattr("src.notifiers.dispatcher._send_telegram", lambda *_: True)
    monkeypatch.setattr("src.notifiers.dispatcher._send_whatsapp", lambda *_: False)

    assert dispatch_message(settings, "mensagem") is False


def test_normalize_chat_id_adds_at_prefix_for_username() -> None:
    assert _normalize_chat_id("EnickJhony") == "@EnickJhony"


def test_normalize_chat_id_keeps_numeric_and_prefixed_values() -> None:
    assert _normalize_chat_id("-1001234567890") == "-1001234567890"
    assert _normalize_chat_id("@canal_teste") == "@canal_teste"
