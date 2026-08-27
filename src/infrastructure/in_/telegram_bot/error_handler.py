import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.shared.application.application_error import ApplicationError

logger = logging.getLogger(__name__)


async def handle_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    error = context.error

    if isinstance(error, ApplicationError):
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(str(error))
        return

    logger.exception(
        "Unexpected error while processing Telegram update",
        exc_info=error,
    )

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."
        )
