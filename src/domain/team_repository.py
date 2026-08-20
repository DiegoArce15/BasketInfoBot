from abc import ABC, abstractmethod

from src.domain.entities import Team, TeamId


class TeamRepository(ABC):
    @abstractmethod
    def save(self, team: Team) -> None:
        """Guarda o actualiza un equipo."""

    @abstractmethod
    def find_by_id(self, team_id: TeamId) -> Team | None:
        """Busca un equipo por su TeamId."""

    @abstractmethod
    def find_by_ids(self, team_ids: list[TeamId]) -> list[Team]:
        """Busca varios equipos por sus TeamId."""

    @abstractmethod
    def find_by_name(self, name: str) -> Team | None:
        """Busca un equipo por su nombre."""

    @abstractmethod
    def find_all(self) -> list[Team]:
        """Retorna todos los equipos registrados."""
