import logging
import os

import uvicorn

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
from src.infrastructure.in_.telegram_bot.webhook import create_webhook_app
from src.infrastructure.out.persistence.postgres_match_persistence import (
    PostgresMatchPersistence,
)
from src.infrastructure.out.persistence.postgres_team_persistence import (
    PostgresTeamPersistence,
)
from src.infrastructure.out.persistence.postgres_user_persistence import (
    PostgresUserPersistence,
)
from src.shared.infrastructure.config.logging_config import configure_logging
from src.shared.infrastructure.config.settings import Settings
from src.shared.infrastructure.system_uuid_generator import (
    SystemUuidGenerator,
)

logger = logging.getLogger(__name__)


def create_app():
    configure_logging()
    logger.info("Starting application initialization")

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
    telegram_app = create_telegram_app(
        bot_token=settings.telegram_bot_token,
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

    # FastAPI + Telegram Webhook
    app = create_webhook_app(
        telegram_app=telegram_app,
        settings=settings,
    )

    logger.info("Application initialized successfully")

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    logger.info("Starting application server on port %d", port)

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
