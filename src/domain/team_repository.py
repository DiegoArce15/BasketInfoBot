from abc import ABC, abstractmethod

from src.domain.team import Team, TeamId


class TeamRepository(ABC):
    @abstractmethod
    def save(self, team: Team) -> None:
        """Save or update a Team"""

    @abstractmethod
    def find_by_id(self, team_id: TeamId) -> Team | None: ...

    @abstractmethod
    def find_by_ids(self, team_ids: list[TeamId]) -> list[Team]: ...

    @abstractmethod
    def find_by_name(self, name: str) -> Team | None: ...

    @abstractmethod
    def find_all(self) -> list[Team]: ...
