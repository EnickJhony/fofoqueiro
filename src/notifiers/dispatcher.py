import logging

from src.config.settings import Settings
from src.notifiers.telegram import send_telegram_message
from src.notifiers.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)



def dispatch_message(settings: Settings, message: str) -> None:
    send_to = settings.send_to

    if send_to == "telegram":
        _send_telegram(settings, message)
    elif send_to == "whatsapp":
        _send_whatsapp(settings, message)
    elif send_to == "ambos":
        _send_telegram(settings, message)
        _send_whatsapp(settings, message)
    else:
        logger.info("Envio desativado. Defina ENVIAR_PARA como telegram, whatsapp ou ambos.")



def _send_telegram(settings: Settings, message: str) -> None:
    try:
        success = send_telegram_message(
            token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
            message=message,
        )
        if not success:
            logger.warning("Telegram nao configurado ou resposta nao foi 200.")
    except Exception as exc:
        logger.exception("Falha no envio para Telegram: %s", exc)



def _send_whatsapp(settings: Settings, message: str) -> None:
    try:
        success = send_whatsapp_message(
            phone=settings.whatsapp_phone,
            apikey=settings.whatsapp_apikey,
            message=message,
        )
        if not success:
            logger.warning("WhatsApp nao configurado ou resposta nao foi 200.")
    except Exception as exc:
        logger.exception("Falha no envio para WhatsApp: %s", exc)
