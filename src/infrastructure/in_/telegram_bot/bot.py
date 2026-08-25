from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
)

from src.application.add_favorite_team_by_telegram_id_use_case import (
    AddFavoriteTeamByTelegramIdUseCase,
)
from src.application.get_available_teams_use_case import GetAvailableTeamsUseCase
from src.application.get_favorite_teams_by_telegram_id_use_case import (
    GetFavoriteTeamsByTelegramIdUseCase,
)
from src.application.get_upcoming_matches_by_telegram_id_use_case import (
    GetUpcomingMatchesByTelegramIdUseCase,
)
from src.application.register_user_use_case import RegisterUserUseCase
from src.application.remove_favorite_team_by_telegram_id_use_case import (
    RemoveFavoriteTeamByTelegramIdUseCase,
)
from src.infrastructure.in_.telegram_bot.handlers import TelegramBotHandlers


def create_telegram_app(
    bot_token: str,
    register_user_use_case: RegisterUserUseCase,
    add_favorite_team_by_telegram_id_use_case: AddFavoriteTeamByTelegramIdUseCase,
    remove_favorite_team_by_telegram_id_use_case: RemoveFavoriteTeamByTelegramIdUseCase,
    get_favorite_teams_by_telegram_id_use_case: GetFavoriteTeamsByTelegramIdUseCase,
    get_available_teams_use_case: GetAvailableTeamsUseCase,
    get_upcoming_matches_by_telegram_id_use_case: GetUpcomingMatchesByTelegramIdUseCase,
) -> Application:

    handlers = TelegramBotHandlers(
        register_user_use_case=register_user_use_case,
        add_favorite_team_by_telegram_id_use_case=(
            add_favorite_team_by_telegram_id_use_case
        ),
        remove_favorite_team_by_telegram_id_use_case=(
            remove_favorite_team_by_telegram_id_use_case
        ),
        get_favorite_teams_by_telegram_id_use_case=(
            get_favorite_teams_by_telegram_id_use_case
        ),
        get_available_teams_use_case=get_available_teams_use_case,
        get_upcoming_matches_by_telegram_id_use_case=(
            get_upcoming_matches_by_telegram_id_use_case
        ),
    )

    app = Application.builder().token(bot_token).updater(None).build()

    # Comandos
    app.add_handler(CommandHandler("start", handlers.start_handler))
    app.add_handler(CommandHandler("favorito", handlers.select_favorite_team_handler))
    app.add_handler(
        CommandHandler("quitarfavorito", handlers.select_remove_favorite_team_handler)
    )
    app.add_handler(CommandHandler("partidos", handlers.upcoming_matches_handler))

    app.add_handler(
        CallbackQueryHandler(handlers.favorite_team_callback_handler, pattern=r"^fav:")
    )

    app.add_handler(
        CallbackQueryHandler(
            handlers.remove_favorite_team_callback_handler, pattern=r"^remove:"
        )
    )

    return app
