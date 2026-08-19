from dataclasses import dataclass
from datetime import datetime

from src.domain.entities import UserId
from src.domain.match_repository import MatchRepository
from src.domain.team_repository import TeamRepository


@dataclass(frozen=True)
class MatchResponseDTO:
    home_team_name: str
    away_team_name: str
    start_time: datetime
    status: str
    channels: list[str] | None = None
    league: str | None = None
    score: str | None = None  # ej: "88 - 85" o None si es SCHEDULED


class GetUpcomingMatchesByUserUseCase:
    def __init__(
        self,
        match_repository: MatchRepository,
        team_repository: TeamRepository,
    ) -> None:
        self._match_repo = match_repository
        self._team_repo = team_repository

    def execute(self, user_id: UserId) -> list[MatchResponseDTO]:
        """Obtiene los próximos partidos de interés para un usuario especifico,

        resolviendo los nombres de los equipos para la capa de presentación.
        """
        # 1. Obtener partidos de interés para el usuario desde el dominio
        matches = self._match_repo.find_upcoming_by_user(user_id)

        # 2. Cargar/Caché ligera de equipos necesarios para evitar consultas redundantes
        team_ids = {m.home_team_id for m in matches} | {m.away_team_id for m in matches}
        teams_map = {
            team_id: self._team_repo.find_by_id(team_id) for team_id in team_ids
        }

        # 3. Construir la lista de DTOs enriquecidos
        response: list[MatchResponseDTO] = []
        for match in matches:
            home_team = teams_map.get(match.home_team_id)
            away_team = teams_map.get(match.away_team_id)

            home_name = home_team.name if home_team else match.home_team_id
            away_name = away_team.name if away_team else match.away_team_id

            score_str = (
                f"{match.score.home} - {match.score.away}" if match.score else None
            )

            response.append(
                MatchResponseDTO(
                    home_team_name=home_name,
                    away_team_name=away_name,
                    start_time=match.start_time,
                    status=match.status.value,
                    channels=match.channels,
                    league=match.league,
                    score=score_str,
                )
            )

        return response
