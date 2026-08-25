from abc import ABC, abstractmethod

from src.domain.match import Match, MatchId
from src.domain.user import UserId


class MatchRepository(ABC):
    @abstractmethod
    def save(self, match: Match) -> None:
        """Save or update a match"""

    @abstractmethod
    def save_all(self, matches: list[Match]) -> None:
        """Save or update multiple matchs"""

    @abstractmethod
    def find_by_id(self, match_id: MatchId) -> Match | None: ...

    @abstractmethod
    def find_upcoming_by_user(self, user_id: UserId) -> list[Match]:
        """Find next Matchs from favorite teams that user has"""
