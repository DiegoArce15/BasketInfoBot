import logging

from src.domain.entities import Team, TelegramId
from src.domain.team_repository import TeamRepository
from src.domain.user_repository import UserRepository

logger = logging.getLogger(__name__)


class GetFavoriteTeamsByTelegramIdUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        team_repository: TeamRepository,
    ) -> None:
        self._user_repository = user_repository
        self._team_repository = team_repository

    def execute(self, telegram_id: TelegramId) -> list[Team]:
        logger.info(
            "Get favorite teams for user with telegram_id=%s", telegram_id.value
        )
        user = self._user_repository.find_by_telegram_id(telegram_id)

        if user is None:
            logger.warning("User with telegram id %s not found", telegram_id.value)
            return []

        team_ids = [favorite.team_id for favorite in user.favorite_teams]

        if not team_ids:
            return []

        return self._team_repository.find_by_ids(team_ids)
