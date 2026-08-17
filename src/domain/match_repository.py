from abc import ABC, abstractmethod

from src.domain.entities import Match, MatchId, MatchStatus, UserId


class MatchRepository(ABC):
    @abstractmethod
    def save(self, match: Match) -> None:
        """Guarda o actualiza un partido."""

    @abstractmethod
    def find_by_id(self, match_id: MatchId) -> Match | None:
        """Busca un partido por su MatchId."""

    @abstractmethod
    def find_upcoming_by_user(self, user_id: UserId) -> list[Match]:
        """Retorna los próximos partidos de interés para un usuario especifico (SCHEDULED)."""

    @abstractmethod
    def find_by_status(self, status: MatchStatus) -> list[Match]:
        """Retorna los partidos filtrados por su estado (ej: LIVE, SCHEDULED)."""
