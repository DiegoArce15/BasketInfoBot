import uuid
from dataclasses import dataclass, field

from src.domain.team import TeamId


@dataclass(frozen=True)
class UserId:
    value: uuid.UUID


@dataclass(frozen=True)
class TelegramId:
    value: int


@dataclass
class User:
    id: UserId
    telegram_id: TelegramId
    username: str | None = None

    @dataclass(frozen=True)
    class FavoriteTeam:
        team_id: TeamId
        notifications_enabled: bool = True

    favorite_teams: list[FavoriteTeam] = field(default_factory=list)

    def has_favorite_team(self, team_id: TeamId) -> bool:
        return any(favorite.team_id == team_id for favorite in self.favorite_teams)

    def remove_favorite_team(self, team_id: TeamId) -> bool:
        favorite_team = next(
            (
                favorite
                for favorite in self.favorite_teams
                if favorite.team_id == team_id
            ),
            None,
        )

        if favorite_team is None:
            return False

        self.favorite_teams.remove(favorite_team)
        return True

    def add_favorite_team(self, team_id: TeamId) -> None:
        self.favorite_teams.append(User.FavoriteTeam(team_id=team_id))
