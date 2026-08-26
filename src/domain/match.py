import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum

from src.domain.team import TeamId


@dataclass(frozen=True)
class MatchId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("MatchId cannot be empty")

    @classmethod
    def create(
        cls,
        home_team: str,
        away_team: str,
        start_time: date | datetime,
    ) -> "MatchId":
        home_team_slug = cls._slugify(home_team)
        away_team_slug = cls._slugify(away_team)
        match_date = start_time.strftime("%Y-%m-%d")

        return cls(value=f"{home_team_slug}-vs-{away_team_slug}-{match_date}")

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.replace("&", " ")
        text = unicodedata.normalize("NFD", text)
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)

        return text.strip("-").lower()

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
            raise ValueError("Score cannot contain negative values")


class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    FINISHED = "FINISHED"


@dataclass
class Match:
    id: MatchId
    home_team_id: TeamId
    away_team_id: TeamId
    start_time: datetime
    channels: list[Channel] = field(default_factory=list)
    league: str | None = None
    status: MatchStatus = MatchStatus.SCHEDULED
    score: Score | None = None
