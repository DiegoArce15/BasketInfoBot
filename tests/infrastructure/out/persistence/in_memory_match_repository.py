
from src.domain.entities import Match, MatchId, MatchStatus, TeamId
from src.domain.match_repository import MatchRepository


class InMemoryMatchRepository(MatchRepository):
    def __init__(self):
        self._matches: dict[MatchId, Match] = {}

    def save(self, match: Match) -> None:
        self._matches[match.id] = match

    def find_by_id(self, match_id: MatchId) -> Match | None:
        return self._matches.get(match_id)

    def find_upcoming_by_team(self, team_id: TeamId) -> list[Match]:
        return [
            match for match in self._matches.values()
            if (match.home_team.id == team_id or match.away_team.id == team_id)
            and match.status == MatchStatus.SCHEDULED
        ]

    def find_by_status(self, status: MatchStatus) -> list[Match]:
        return [
            match for match in self._matches.values()
            if match.status == status
        ]