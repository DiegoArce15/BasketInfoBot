from abc import ABC, abstractmethod

from src.application.sync_upcoming_matches_command import SyncMatchCommand


class MatchFetcher(ABC):
    @abstractmethod
    def fetch_upcoming_matches(self) -> list[SyncMatchCommand]:
        """Fetch upcoming matches from the configured external source"""
