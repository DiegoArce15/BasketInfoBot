import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TeamId:
    value: uuid.UUID


@dataclass
class Team:
    id: TeamId
    name: str
    short_name: str
    country: str | None = None
    logo_url: str | None = None
