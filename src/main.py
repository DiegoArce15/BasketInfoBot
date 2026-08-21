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
from src.infrastructure.in_.telegram_bot.bot import create_telegram_app
from src.infrastructure.out.persistence.postgres_match_persistence import (
    PostgresMatchPersistence,
)
from src.infrastructure.out.persistence.postgres_team_persistence import (
    PostgresTeamPersistence,
)
from src.infrastructure.out.persistence.postgres_user_persistence import (
    PostgresUserPersistence,
)
from src.shared.infrastructure.config.settings import Settings
from src.shared.infrastructure.system_uuid_generator import (
    SystemUuidGenerator,
)


def main() -> None:
    settings = Settings()

    # Infrastructure
    user_repository = PostgresUserPersistence(settings.database_url)
    team_repository = PostgresTeamPersistence(settings.database_url)
    match_repository = PostgresMatchPersistence(settings.database_url)
    id_generator = SystemUuidGenerator()

    # Application
    add_favorite_team_by_telegram_id_use_case = AddFavoriteTeamByTelegramIdUseCase(
        user_repo=user_repository,
        team_repo=team_repository,
    )

    get_available_teams_use_case = GetAvailableTeamsUseCase(
        team_repo=team_repository,
    )

    get_favorite_teams_by_telegram_id_use_case = GetFavoriteTeamsByTelegramIdUseCase(
        user_repository=user_repository,
        team_repository=team_repository,
    )

    get_upcoming_matches_by_telegram_id_use_case = (
        GetUpcomingMatchesByTelegramIdUseCase(
            user_repo=user_repository,
            match_repo=match_repository,
            team_repo=team_repository,
        )
    )

    register_user_use_case = RegisterUserUseCase(
        user_repository=user_repository,
        id_generator=id_generator,
    )

    remove_favorite_team_by_telegram_id_use_case = (
        RemoveFavoriteTeamByTelegramIdUseCase(
            user_repo=user_repository,
            team_repo=team_repository,
        )
    )

    # Telegram
    app = create_telegram_app(
        bot_token=settings.telegram_bot_token,
        register_user_use_case=register_user_use_case,
        add_favorite_team_by_telegram_id_use_case=add_favorite_team_by_telegram_id_use_case,
        remove_favorite_team_by_telegram_id_use_case=remove_favorite_team_by_telegram_id_use_case,
        get_favorite_teams_by_telegram_id_use_case=get_favorite_teams_by_telegram_id_use_case,
        get_available_teams_use_case=get_available_teams_use_case,
        get_upcoming_matches_by_telegram_id_use_case=get_upcoming_matches_by_telegram_id_use_case,
    )

    print("Bot iniciado. Esperando mensajes de Telegram...")
    app.run_polling()


if __name__ == "__main__":
    main()
