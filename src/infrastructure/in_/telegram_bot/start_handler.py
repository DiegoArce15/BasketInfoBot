from telegram import Update
from telegram.ext import ContextTypes

from src.application.register_user_use_case import RegisterUserUseCase
from src.domain.user import TelegramId


class StartHandler:
    def __init__(self, register_user_use_case: RegisterUserUseCase) -> None:
        self.register_user_use_case = register_user_use_case

    async def handle(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        """Comando /start."""
        user = update.effective_user

        if not user or not update.message:
            return

        self.register_user_use_case.execute(
            telegram_id=TelegramId(user.id),
            username=user.username,
        )

        await update.message.reply_text(
            f"¡Hola {user.first_name}! 🏀\n"
            "Te has registrado correctamente en BasketInfoBot.\n\n"
            "Comandos disponibles:\n"
            "• `/favorito` - Añadir un equipo a favoritos\n"
            "• `/quitarfavorito` - Quitar un equipo de favoritos\n"
            "• `/partidos` - Ver tus próximos partidos",
            parse_mode="Markdown",
        )
