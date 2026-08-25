import uuid

from src.domain.entities import Team, TeamId


def a_team(
    *,
    id: TeamId | None = None,
    name: str | None = None,
    short_name: str | None = None,
) -> Team:
    return Team(
        id=id or TeamId(uuid.uuid4()),
        name=name or f"Team {uuid.uuid4().hex[:8]}",
        short_name=short_name or uuid.uuid4().hex[:3].upper(),
    )
