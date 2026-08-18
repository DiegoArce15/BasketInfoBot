from dataclasses import dataclass
from datetime import datetime

from src.domain.entities import Match, MatchId, MatchStatus, Score, TeamId
from src.domain.match_repository import MatchRepository


@dataclass(frozen=True)
class ScrapedMatchDTO:
    home_team_id: TeamId
    away_team_id: TeamId
    start_time: datetime
    status: str  # Ej: "SCHEDULED", "FINISHED", "CANCELLED"
    home_score: int | None = None
    away_score: int | None = None
    channels: list[str] | None = None
    league: str | None = None


class ProcessScrapedMatchesUseCase:
    def __init__(self, match_repository: MatchRepository) -> None:
        self._match_repository = match_repository

    def execute(self, dto: ScrapedMatchDTO) -> Match:
        """Procesa un único partido scrapeado y lo persiste."""
        # 1. Generar MatchId determinista (ej: real-madrid-vs-barcelona-2026-10-25)
        match_id = MatchId.create(
            home_team_id=dto.home_team_id,
            away_team_id=dto.away_team_id,
            start_time=dto.start_time,
        )

        # 2. Construir el Value Object Score si hay marcador
        score: Score | None = None
        if dto.home_score is not None and dto.away_score is not None:
            score = Score(home=dto.home_score, away=dto.away_score)

        # 3. Crear Entidad de Dominio
        match = Match(
            id=match_id,
            home_team_id=dto.home_team_id,
            away_team_id=dto.away_team_id,
            score=score,
            channels=dto.channels,
            league=dto.league,
            start_time=dto.start_time,
            status=MatchStatus(dto.status),
        )

        # 4. Guardar en repositorio (UPSERT)
        self._match_repository.save(match)

        return match
