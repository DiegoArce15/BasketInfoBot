from src.domain.entities import TeamId, UserId
from src.domain.team_repository import TeamRepository
from src.domain.user_repository import UserRepository


class AddFavoriteTeamUseCase:
    """Añade un equipo a la lista de favoritos de un usuario."""

    def __init__(self, user_repo: UserRepository, team_repo: TeamRepository):
        self.user_repo = user_repo
        self.team_repo = team_repo

    def execute(self, user_id: UserId, team_id: TeamId) -> None:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id.value} no encontrado.")

        team = self.team_repo.find_by_id(team_id)
        if not team:
            raise ValueError(f"El equipo {team_id.value} no existe.")

        if team_id not in user.favorite_team_ids:
            user.favorite_team_ids.append(team_id)
            self.user_repo.save(user)