from dataclasses import dataclass
from datetime import datetime

from src.domain.entities import Channel, MatchStatus, Score


@dataclass(frozen=True)
class SyncMatchCommand:
    home_team_name: str
    away_team_name: str
    channels: list[Channel]
    league: str
    status: MatchStatus
    start_time: datetime | None
    score: Score | None = None
