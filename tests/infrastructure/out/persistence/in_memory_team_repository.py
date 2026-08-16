
from src.domain.entities import Team, TeamId
from src.domain.team_repository import TeamRepository


class InMemoryTeamRepository(TeamRepository):
    def __init__(self):
        self._teams: dict[TeamId, Team] = {}

    def save(self, team: Team) -> None:
        self._teams[team.id] = team

    def find_by_id(self, team_id: TeamId) -> Team | None:
        return self._teams.get(team_id)

    def search_by_name(self, name_query: str) -> list[Team]:
        query = name_query.lower()
        return [
            team for team in self._teams.values()
            if query in team.name.lower()
        ]

    def find_all(self) -> list[Team]:
        return list(self._teams.values())