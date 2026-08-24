import logging

from src.domain.entities import TeamId, TelegramId, User
from src.domain.team_repository import TeamRepository
from src.domain.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AddFavoriteTeamByTelegramIdUseCase:
    def __init__(self, user_repo: UserRepository, team_repo: TeamRepository):
        self._user_repo = user_repo
        self._team_repo = team_repo

    def execute(self, telegram_id: TelegramId, team_id: TeamId) -> None:
        logger.info(
            "Adding favorite team %s for user with telegram id %s",
            team_id.value,
            telegram_id.value,
        )
        user = self._get_user_or_throw(telegram_id)
        self._check_team_exists_or_throw(team_id)

        if user.has_favorite_team(team_id):
            logger.info(
                "Team %s is already a favorite for user with telegram id %s",
                team_id.value,
                telegram_id.value,
            )
            return

        user.add_favorite_team(team_id)
        self._user_repo.save(user)

    def _get_user_or_throw(self, telegram_id: TelegramId) -> User:
        user = self._user_repo.find_by_telegram_id(telegram_id)

        if user is None:
            raise ValueError(f"User with telegram id {telegram_id.value} not found")

        return user

    def _check_team_exists_or_throw(self, team_id: TeamId) -> None:
        if self._team_repo.find_by_id(team_id) is None:
            raise ValueError(f"Team {team_id.value} not found")
