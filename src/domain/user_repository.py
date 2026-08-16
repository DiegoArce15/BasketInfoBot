from abc import ABC, abstractmethod

from src.domain.entities import TeamId, User, UserId


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        """Guarda o actualiza un usuario en la persistencia."""

    @abstractmethod
    def find_by_id(self, user_id: UserId) -> User | None:
        """Busca un usuario por su UserId."""

    @abstractmethod
    def find_users_by_favorite_team(self, team_id: TeamId) -> list[User]:
        """Retorna la lista de usuarios que siguen a un equipo en concreto."""
