from src.domain.entities import TeamId, TelegramId, User
from src.domain.team_repository import TeamRepository
from src.domain.user_repository import UserRepository


class AddFavoriteTeamByTelegramIdUseCase:
    def __init__(self, user_repo: UserRepository, team_repo: TeamRepository):
        self._user_repo = user_repo
        self._team_repo = team_repo

    def execute(self, telegram_id: TelegramId, team_id: TeamId) -> None:
        user = self._user_repo.find_by_telegram_id(telegram_id)

        if user is None:
            raise ValueError(
                f"Usuario con telegram id {telegram_id.value} no encontrado"
            )

        team = self._team_repo.find_by_id(team_id)

        if team is None:
            raise ValueError(f"El equipo {team_id.value} no existe")

        if any(favorite.team_id == team_id for favorite in user.favorite_teams):
            return

        user.favorite_teams.append(User.FavoriteTeam(team_id=team_id))

        self._user_repo.save(user)

        favorite_team = User.FavoriteTeam(team_id=team_id)

        if favorite_team not in user.favorite_teams:
            user.favorite_teams.append(favorite_team)
            self._user_repo.save(user)
