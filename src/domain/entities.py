from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# ------------------------------------------------------------------
# Value Objects (Identificadores)
# ------------------------------------------------------------------

@dataclass(frozen=True)
class UserId:
    value: int  # Usualmente el chat_id de Telegram


@dataclass(frozen=True)
class TeamId:
    value: str  # ej: "real-madrid", "fc-barcelona"


@dataclass(frozen=True)
class MatchId:
    value: str  # ej: "2026-08-20-rm-barca"


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"


# ------------------------------------------------------------------
# Entities
# ------------------------------------------------------------------

@dataclass
class Team:
    id: TeamId
    name: str
    country: str | None = None
    logo_url: str | None = None


@dataclass
class Match:
    id: MatchId
    home_team: Team
    away_team: Team
    start_time: datetime
    channel: str
    league: str
    status: MatchStatus = MatchStatus.SCHEDULED


@dataclass
class User:
    id: UserId
    username: str | None = None
    favorite_team_ids: list[TeamId] = field(default_factory=list)