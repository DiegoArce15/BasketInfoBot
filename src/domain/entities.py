import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum

# ------------------------------------------------------------------
# Value Objects (Identificadores)
# ------------------------------------------------------------------


@dataclass(frozen=True)
class UserId:
    value: uuid.UUID


@dataclass(frozen=True)
class TelegramId:
    value: int


@dataclass(frozen=True)
class TeamId:
    value: uuid.UUID


@dataclass(frozen=True)
class MatchId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("El MatchId no puede estar vacío.")

    @classmethod
    def create(
        cls, home_team_id: TeamId, away_team_id: TeamId, start_time: date | datetime
    ) -> "MatchId":
        """
        Genera un MatchId determinista y legible.
        Ejemplo: real-madrid-vs-barcelona-2026-10-25
        """
        date_str = (
            start_time.strftime("%Y-%m-%d")
            if isinstance(start_time, (date, datetime))
            else str(start_time)
        )
        formatted_id = (
            f"{home_team_id.value}-vs-{away_team_id.value}-{date_str}".lower().strip()
        )
        return cls(value=formatted_id)

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class Channel:
    name: str


@dataclass(frozen=True)
class Score:
    home: int
    away: int

    def __post_init__(self) -> None:
        if self.home < 0 or self.away < 0:
            raise ValueError("El marcador no puede contener valores negativos.")


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------


class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    FINISHED = "FINISHED"
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
    home_team_id: TeamId
    away_team_id: TeamId
    start_time: datetime
    score: Score | None = None
    channels: list[Channel] = field(default_factory=list)
    league: str | None = None
    status: MatchStatus = MatchStatus.SCHEDULED


@dataclass
class User:
    id: UserId
    telegram_id: TelegramId | None
    username: str | None = None

    @dataclass(frozen=True)
    class FavoriteTeam:
        team_id: TeamId
        notifications_enabled: bool = True

    favorite_teams: list[FavoriteTeam] = field(default_factory=list)
