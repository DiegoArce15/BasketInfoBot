import random
import uuid

from src.domain.team import TeamId
from src.domain.user import TelegramId, User, UserId


def an_user(
    *,
    id: UserId | None = None,
    telegram_id: TelegramId | None = None,
    username: str | None = None,
    favorite_teams: list[TeamId] | None = None,
) -> User:
    return User(
        id=id or UserId(uuid.uuid4()),
        telegram_id=telegram_id or TelegramId(random.randint(100000000, 999999999)),
        username=username or f"user-{uuid.uuid4().hex[:8]}",
        favorite_teams=[
            User.FavoriteTeam(team_id=team_id) for team_id in (favorite_teams or [])
        ],
    )
