import re
import unicodedata
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

    @staticmethod
    def _slugify(text: str) -> str:
        """
        Transforma 'Río Breogán' o 'Kids&Us Manresa' en 'rio-breogan' o 'kids-us-manresa'.
        """
        # 1. Reemplazar '&' por espacio para evitar que las palabras se junten
        text = text.replace("&", " ")

        # 2. Normalizar acentos y diacríticos
        text = unicodedata.normalize("NFD", text)
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")

        # 3. Eliminar caracteres especiales
        text = re.sub(r"[^\w\s-]", "", text)

        # 4. Reemplazar espacios múltiples por un solo guion
        text = re.sub(r"[-\s]+", "-", text).strip("-")

        return text.lower()

    @classmethod
    def create(
        cls, home_team: str, away_team: str, start_time: date | datetime
    ) -> "MatchId":
        """
        Genera un MatchId determinista, limpio y legible.
        Ejemplo: 'Río Breogán' vs 'Kids&Us Manresa' -> 'rio-breogan-vs-kids-us-manresa-2026-09-26'
        """
        home_slug = cls._slugify(home_team)
        away_slug = cls._slugify(away_team)

        date_str = (
            start_time.strftime("%Y-%m-%d")
            if isinstance(start_time, (date, datetime))
            else str(start_time)
        )

        formatted_id = f"{home_slug}-vs-{away_slug}-{date_str}"
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


# ------------------------------------------------------------------
# Entities
# ------------------------------------------------------------------


@dataclass
class Team:
    id: TeamId
    name: str
    short_name: str
    country: str | None = None
    logo_url: str | None = None


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
