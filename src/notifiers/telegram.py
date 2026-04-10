from urllib.parse import quote_plus
from urllib.request import Request, urlopen



def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = f"chat_id={quote_plus(chat_id)}&text={quote_plus(message)}"

    request = Request(url, data=payload.encode("utf-8"), method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")

    with urlopen(request, timeout=20) as response:
        return response.status == 200
