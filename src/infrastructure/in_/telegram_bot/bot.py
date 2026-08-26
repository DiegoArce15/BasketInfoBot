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
from src.infrastructure.in_.telegram_bot.remove_favorite_teams_handler import (
    RemoveFavoriteTeamHandler,
)
from src.infrastructure.in_.telegram_bot.select_favorite_teams_handler import (
    SelectFavoriteTeamHandler,
)
from src.infrastructure.in_.telegram_bot.start_handler import StartHandler
from src.infrastructure.in_.telegram_bot.upcoming_matches_for_user_handler import (
    UpcomingMatchesForUserHandler,
)


def create_telegram_app(
    bot_token: str,
    register_user_use_case: RegisterUserUseCase,
    add_favorite_team_by_telegram_id_use_case: AddFavoriteTeamByTelegramIdUseCase,
    remove_favorite_team_by_telegram_id_use_case: RemoveFavoriteTeamByTelegramIdUseCase,
    get_favorite_teams_by_telegram_id_use_case: GetFavoriteTeamsByTelegramIdUseCase,
    get_available_teams_use_case: GetAvailableTeamsUseCase,
    get_upcoming_matches_by_telegram_id_use_case: GetUpcomingMatchesByTelegramIdUseCase,
) -> Application:
    start_handler = StartHandler(register_user_use_case)
    select_favorite_teams_handler = SelectFavoriteTeamHandler(
        get_available_teams_use_case=get_available_teams_use_case,
        add_favorite_team_by_telegram_id_use_case=add_favorite_team_by_telegram_id_use_case,
    )
    remove_favorite_team_handler = RemoveFavoriteTeamHandler(
        get_favorite_teams_by_telegram_id_use_case=get_favorite_teams_by_telegram_id_use_case,
        remove_favorite_team_by_telegram_id_use_case=remove_favorite_team_by_telegram_id_use_case,
    )
    upcoming_matches_for_user_handler = UpcomingMatchesForUserHandler(
        get_upcoming_matches_by_telegram_id_use_case=(
            get_upcoming_matches_by_telegram_id_use_case
        ),
    )

    app = Application.builder().token(bot_token).updater(None).build()

    # Comandos
    app.add_handler(CommandHandler("start", start_handler.handle))
    app.add_handler(CommandHandler("favorito", select_favorite_teams_handler.handle))
    app.add_handler(
        CommandHandler("quitarfavorito", remove_favorite_team_handler.handle)
    )
    app.add_handler(
        CommandHandler("partidos", upcoming_matches_for_user_handler.handle)
    )

    app.add_handler(
        CallbackQueryHandler(
            select_favorite_teams_handler.callback_handle, pattern=r"^fav:"
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            remove_favorite_team_handler.callback_handle, pattern=r"^remove:"
        )
    )

    return app
