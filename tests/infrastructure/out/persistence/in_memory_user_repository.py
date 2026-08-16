
from src.domain.entities import TeamId, User, UserId
from src.domain.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: dict[UserId, User] = {}

    def save(self, user: User) -> None:
        self._users[user.id] = user

    def find_by_id(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

    def find_users_by_favorite_team(self, team_id: TeamId) -> list[User]:
        return [
            user for user in self._users.values()
            if team_id in user.favorite_team_ids
        ]
