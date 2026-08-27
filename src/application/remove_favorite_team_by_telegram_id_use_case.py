import logging

from src.domain.team import TeamId
from src.domain.team_repository import TeamRepository
from src.domain.user import TelegramId, User
from src.domain.user_repository import UserRepository
from src.shared.application.application_error import ApplicationError

logger = logging.getLogger(__name__)


class RemoveFavoriteTeamByTelegramIdUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        team_repo: TeamRepository,
    ) -> None:
        self._user_repo = user_repo
        self._team_repo = team_repo

    def execute(
        self,
        telegram_id: TelegramId,
        team_id: TeamId,
    ) -> None:
        logger.info(
            "Remove favorite team %s for user with telegram_id=%s",
            team_id.value,
            telegram_id.value,
        )
        user = self._get_user_or_throw(telegram_id)
        self._check_team_exists(team_id)

        if not user.remove_favorite_team(team_id):
            return

        self._user_repo.save(user)

        logger.info(
            "Favorite team removed, telegram_id=%s, team_id=%s",
            telegram_id.value,
            team_id.value,
        )

    def _get_user_or_throw(self, telegram_id: TelegramId) -> User:
        user = self._user_repo.find_by_telegram_id(telegram_id)

        if user is None:
            raise ApplicationError(
                f"User with telegram id {telegram_id.value} not found"
            )

        return user

    def _check_team_exists(self, team_id: TeamId) -> None:
        if self._team_repo.find_by_id(team_id) is None:
            raise ApplicationError(f"Team {team_id.value} not found")
