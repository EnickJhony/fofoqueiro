import logging

from src.config.settings import Settings
from src.notifiers.telegram import send_telegram_message
from src.notifiers.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)



def dispatch_message(settings: Settings, message: str) -> bool:
    send_to = settings.send_to

    if send_to == "telegram":
        return _send_telegram(settings, message)
    elif send_to == "whatsapp":
        return _send_whatsapp(settings, message)
    elif send_to == "ambos":
        telegram_ok = _send_telegram(settings, message)
        whatsapp_ok = _send_whatsapp(settings, message)
        return telegram_ok and whatsapp_ok
    else:
        logger.info("Envio desativado. Defina ENVIAR_PARA como telegram, whatsapp ou ambos.")
        return False



def _send_telegram(settings: Settings, message: str) -> bool:
    chat_ids = settings.telegram_chat_ids

    if not chat_ids and settings.telegram_chat_id:
        chat_ids = [settings.telegram_chat_id]

    if not chat_ids:
        logger.warning("Telegram nao configurado: nenhum TELEGRAM_CHAT_ID(S) definido.")
        return False

    any_success = False
    all_success = True

    for chat_id in chat_ids:
        try:
            success = send_telegram_message(
                token=settings.telegram_bot_token,
                chat_id=chat_id,
                message=message,
            )
            if not success:
                all_success = False
                logger.warning("Falha ao enviar para chat_id=%s no Telegram.", chat_id)
            else:
                any_success = True
        except Exception as exc:
            all_success = False
            logger.exception("Falha no envio para Telegram (chat_id=%s): %s", chat_id, exc)

    return any_success and all_success



def _send_whatsapp(settings: Settings, message: str) -> bool:
    try:
        success = send_whatsapp_message(
            phone=settings.whatsapp_phone,
            apikey=settings.whatsapp_apikey,
            message=message,
        )
        if not success:
            logger.warning("WhatsApp nao configurado ou resposta nao foi 200.")
        return success
    except Exception as exc:
        logger.exception("Falha no envio para WhatsApp: %s", exc)
        return False
