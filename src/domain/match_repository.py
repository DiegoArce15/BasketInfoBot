from abc import ABC, abstractmethod

from src.domain.entities import Match, MatchId, MatchStatus, TeamId


class MatchRepository(ABC):
    @abstractmethod
    def save(self, match: Match) -> None:
        """Guarda o actualiza un partido."""

    @abstractmethod
    def find_by_id(self, match_id: MatchId) -> Match | None:
        """Busca un partido por su MatchId."""

    @abstractmethod
    def find_upcoming_by_team(self, team_id: TeamId) -> list[Match]:
        """Retorna los próximos partidos de un equipo (SCHEDULED)."""

    @abstractmethod
    def find_by_status(self, status: MatchStatus) -> list[Match]:
        """Retorna los partidos filtrados por su estado (ej: LIVE, SCHEDULED)."""
