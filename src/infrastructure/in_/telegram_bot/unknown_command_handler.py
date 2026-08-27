from telegram import Update
from telegram.ext import ContextTypes


class UnknownCommandHandler:
    async def handle(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.message:
            await update.message.reply_text(
                "No reconozco ese comando. "
                "Puedes usar /ayuda para ver los comandos disponibles"
            )
