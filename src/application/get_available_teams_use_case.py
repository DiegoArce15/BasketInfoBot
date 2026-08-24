from src.domain.entities import Team
from src.domain.team_repository import TeamRepository


class GetAvailableTeamsUseCase:
    def __init__(self, team_repo: TeamRepository):
        self.team_repo = team_repo

    def execute(self) -> list[Team]:
        return self.team_repo.find_all()
