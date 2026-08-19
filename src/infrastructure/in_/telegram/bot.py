from telegram.ext import Application, ApplicationBuilder, CommandHandler

from src.application.add_favorite_team_use_case import AddFavoriteTeamUseCase
from src.application.get_upcoming_matches_by_user_use_case import (
    GetUpcomingMatchesByUserUseCase,
)
from src.application.register_user_use_case import RegisterUserUseCase
from src.infrastructure.in_.telegram.handlers import TelegramBotHandlers


def create_telegram_app(
    bot_token: str,
    register_user_use_case: RegisterUserUseCase,
    add_favorite_team_use_case: AddFavoriteTeamUseCase,
    get_upcoming_matches_use_case: GetUpcomingMatchesByUserUseCase,
) -> Application:
    """Instancia y configura los handlers de la aplicación de Telegram."""

    handlers = TelegramBotHandlers(
        register_user_use_case=register_user_use_case,
        add_favorite_team_use_case=add_favorite_team_use_case,
        get_upcoming_matches_use_case=get_upcoming_matches_use_case,
    )

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", handlers.start_handler))
    app.add_handler(CommandHandler("favorito", handlers.add_favorite_handler))
    app.add_handler(CommandHandler("partidos", handlers.upcoming_matches_handler))

    return app
