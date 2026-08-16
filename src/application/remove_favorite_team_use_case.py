from src.domain.entities import TeamId, UserId
from src.domain.user_repository import UserRepository


class RemoveFavoriteTeamUseCase:
    """Elimina un equipo de los favoritos del usuario."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: UserId, team_id: TeamId) -> None:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id.value} no encontrado.")

        if team_id in user.favorite_team_ids:
            user.favorite_team_ids.remove(team_id)
            self.user_repo.save(user)