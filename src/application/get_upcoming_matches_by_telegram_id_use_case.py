from dataclasses import dataclass
from datetime import datetime

from src.domain.entities import TelegramId
from src.domain.match_repository import MatchRepository
from src.domain.team_repository import TeamRepository
from src.domain.user_repository import UserRepository


@dataclass(frozen=True)
class MatchResponseDTO:
    home_team_name: str
    away_team_name: str
    start_time: datetime
    status: str
    channels: list[str] | None = None
    league: str | None = None
    score: str | None = None  # ej: "88 - 85" o None si es SCHEDULED


class GetUpcomingMatchesByTelegramIdUseCase:
    """Obtiene los próximos partidos de los equipos favoritos de un usuario."""

    def __init__(
        self,
        user_repo: UserRepository,
        match_repo: MatchRepository,
        team_repo: TeamRepository,
    ):
        self._user_repo = user_repo
        self._match_repo = match_repo
        self._team_repo = team_repo

    def execute(self, telegram_id: TelegramId) -> list[MatchResponseDTO]:
        user = self._user_repo.find_by_telegram_id(telegram_id)

        if user is None:
            return []

        matches = self._match_repo.find_upcoming_by_user(user.id)

        if not matches:
            return []

        # Obtener los equipos una sola vez para evitar consultas redundantes.
        team_ids = {match.home_team_id for match in matches} | {
            match.away_team_id for match in matches
        }

        teams_by_id = {
            team_id: self._team_repo.find_by_id(team_id) for team_id in team_ids
        }

        responses = []

        for match in matches:
            home_team = teams_by_id[match.home_team_id]
            away_team = teams_by_id[match.away_team_id]

            if home_team is None or away_team is None:
                continue

            score = None
            if match.score is not None:
                score = f"{match.score.home} - {match.score.away}"

            responses.append(
                MatchResponseDTO(
                    home_team_name=home_team.name,
                    away_team_name=away_team.name,
                    start_time=match.start_time,
                    status=match.status.value,
                    channels=[channel.name for channel in match.channels],
                    league=match.league,
                    score=score,
                )
            )

        return responses
