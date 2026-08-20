from src.domain.entities import Match, MatchId
from src.domain.match_fetcher import MatchFetcher
from src.domain.match_repository import MatchRepository
from src.domain.team_repository import TeamRepository


class SyncUpcomingMatchesUseCase:
    """Sincroniza los próximos partidos obtenidos de una fuente externa."""

    def __init__(
        self,
        match_fetcher: MatchFetcher,
        match_repository: MatchRepository,
        team_repository: TeamRepository,
    ) -> None:
        self._match_fetcher = match_fetcher
        self._match_repository = match_repository
        self._team_repository = team_repository

    def execute(self) -> int:
        commands = self._match_fetcher.fetch_upcoming_matches()

        synchronized_matches = 0

        for command in commands:
            home_team = self._team_repository.find_by_name(command.home_team_name)
            if home_team is None:
                raise ValueError(
                    f"Equipo local no encontrado: {command.home_team_name}"
                )

            away_team = self._team_repository.find_by_name(command.away_team_name)
            if away_team is None:
                raise ValueError(
                    f"Equipo visitante no encontrado: {command.away_team_name}"
                )

            match = Match(
                id=MatchId.create(
                    home_team=command.home_team_name,
                    away_team=command.away_team_name,
                    start_time=command.start_time,
                ),
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                start_time=command.start_time,
                channels=command.channels,
                league=command.league,
                status=command.status,
                score=command.score,
            )

            self._match_repository.save(match)
            synchronized_matches += 1

        return synchronized_matches
