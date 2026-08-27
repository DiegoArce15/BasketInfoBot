from telegram import Update
from telegram.ext import ContextTypes


class HelpHandler:
    async def handle(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if not update.message:
            return

        await update.message.reply_text(
            "🏀 Comandos disponibles:\n\n"
            "• /start - Registrarte en BasketInfoBot\n"
            "• /favorito - Añadir un equipo a favoritos\n"
            "• /quitarfavorito - Quitar un equipo de favoritos\n"
            "• /partidos - Ver tus próximos partidos\n"
            "• /ayuda - Mostrar esta ayuda"
        )
