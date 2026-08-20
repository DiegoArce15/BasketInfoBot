from src.domain.entities import Team, TelegramId
from src.domain.team_repository import TeamRepository
from src.domain.user_repository import UserRepository


class GetFavoriteTeamsByTelegramIdUseCase:
    """Obtiene los equipos favoritos de un usuario de Telegram."""

    def __init__(
        self,
        user_repository: UserRepository,
        team_repository: TeamRepository,
    ) -> None:
        self._user_repository = user_repository
        self._team_repository = team_repository

    def execute(self, telegram_id: TelegramId) -> list[Team]:
        user = self._user_repository.find_by_telegram_id(telegram_id)

        if user is None:
            return []

        team_ids = [favorite.team_id for favorite in user.favorite_teams]

        if not team_ids:
            return []

        return self._team_repository.find_by_ids(team_ids)
