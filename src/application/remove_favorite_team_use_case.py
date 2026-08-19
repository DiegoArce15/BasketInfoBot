from src.domain.entities import TeamId, UserId
from src.domain.team_repository import TeamRepository
from src.domain.user_repository import UserRepository


class RemoveFavoriteTeamUseCase:
    """Elimina un equipo de los favoritos del usuario."""

    def __init__(self, user_repo: UserRepository, team_repo: TeamRepository):
        self.user_repo = user_repo
        self.team_repo = team_repo

    def execute(self, user_id: UserId, team_id: TeamId) -> None:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con id {user_id.value} no encontrado")

        team = self.team_repo.find_by_id(team_id)
        if not team:
            raise ValueError(f"Equipo con id {team_id.value} no encontrado")

        team_to_remove = next(
            (fav for fav in user.favorite_teams if fav.team_id == team_id), None
        )

        if team_to_remove:
            user.favorite_teams.remove(team_to_remove)
            self.user_repo.save(user)
