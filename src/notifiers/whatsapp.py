from urllib.parse import quote_plus
from urllib.request import urlopen



def send_whatsapp_message(phone: str, apikey: str, message: str) -> bool:
    if not phone or not apikey:
        return False

    url = (
        "https://api.callmebot.com/whatsapp.php"
        f"?phone={quote_plus(phone)}&text={quote_plus(message)}&apikey={quote_plus(apikey)}"
    )

    with urlopen(url, timeout=20) as response:
        return response.status == 200
