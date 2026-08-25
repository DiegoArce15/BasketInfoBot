import random
import uuid
from datetime import UTC, datetime, timedelta

from src.domain.match import (
    Channel,
    Match,
    MatchId,
    MatchStatus,
    Score,
)
from src.domain.team import TeamId


def a_match(
    *,
    id: MatchId | None = None,
    home_team_id: TeamId | None = None,
    away_team_id: TeamId | None = None,
    start_time: datetime | None = None,
    score: Score | None = None,
    status: MatchStatus = MatchStatus.SCHEDULED,
    channels: list[Channel] | None = None,
    league: str | None = None,
) -> Match:
    return Match(
        id=id or MatchId(f"match-{uuid.uuid4().hex[:8]}"),
        home_team_id=home_team_id or TeamId(uuid.uuid4()),
        away_team_id=away_team_id or TeamId(uuid.uuid4()),
        start_time=start_time or _random_datetime(),
        score=score,
        status=status,
        channels=channels or [],
        league=league,
    )


def _random_datetime() -> datetime:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = datetime(2030, 12, 31, tzinfo=UTC)

    seconds = random.randint(
        0,
        int((end - start).total_seconds()),
    )

    return start + timedelta(seconds=seconds)
