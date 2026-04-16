import json
from urllib.error import HTTPError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


MAX_TELEGRAM_MESSAGE_LENGTH = 4096


def _normalize_chat_id(chat_id: str) -> str:
    value = chat_id.strip()

    if not value:
        return value

    if value.startswith("@") or value.startswith("-") or value.isdigit():
        return value

    return f"@{value}"


def _split_message(message: str, max_length: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> list[str]:
    if not message:
        return []

    chunks: list[str] = []
    current_chunk = ""

    for line in message.splitlines(keepends=True):
        if len(line) > max_length:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            for start in range(0, len(line), max_length):
                chunks.append(line[start : start + max_length])
            continue

        if len(current_chunk) + len(line) <= max_length:
            current_chunk += line
        else:
            chunks.append(current_chunk)
            current_chunk = line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks



def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    if not token or not chat_id or not message:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    normalized_chat_id = _normalize_chat_id(chat_id)

    for chunk in _split_message(message):
        payload = f"chat_id={quote_plus(normalized_chat_id)}&text={quote_plus(chunk)}"

        request = Request(url, data=payload.encode("utf-8"), method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urlopen(request, timeout=20) as response:
                if response.status != 200:
                    return False
        except HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            description = body

            try:
                parsed_body = json.loads(body)
                description = parsed_body.get("description", body)
            except json.JSONDecodeError:
                pass

            raise RuntimeError(f"Telegram API retornou {exc.code}: {description}") from exc

    return True
