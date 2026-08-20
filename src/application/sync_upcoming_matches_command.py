from dataclasses import dataclass
from datetime import datetime

from src.domain.entities import Channel, MatchStatus, Score


@dataclass(frozen=True)
class SyncMatchCommand:
    home_team_name: str
    away_team_name: str
    start_time: datetime
    channels: list[Channel]
    league: str
    status: MatchStatus
    score: Score | None = None
