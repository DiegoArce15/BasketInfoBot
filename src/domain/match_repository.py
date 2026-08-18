from abc import ABC, abstractmethod

from src.domain.entities import Match, MatchId, UserId


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
