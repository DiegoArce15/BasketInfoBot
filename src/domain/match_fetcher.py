from abc import ABC, abstractmethod

from domain.entities import Match


class MatchFetcher(ABC):
    @abstractmethod
    def fetch_upcoming_matches(self) -> list[Match]:
        """Extrae y devuelve los próximos partidos disponibles."""
