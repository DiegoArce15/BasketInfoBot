import logging
import time

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.domain.match import Match, MatchId
from src.domain.match_fetcher import MatchFetcher
from src.domain.match_repository import MatchRepository
from src.domain.team import Team
from src.domain.team_repository import TeamRepository

logger = logging.getLogger(__name__)


class SyncUpcomingMatchesUseCase:
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
        logger.info("Starting upcoming matches synchronization")

        commands = self._match_fetcher.fetch_upcoming_matches()

        logger.info("Fetched %d upcoming matches", len(commands))

        teams_by_name = self._load_teams_by_name()
        matches = self._build_matches(commands, teams_by_name)

        logger.info("Prepared %d matches to save", len(matches))

        self._save_matches(matches)

        logger.info(
            "Upcoming matches synchronization completed: %d matches synchronized",
            len(matches),
        )

        return len(matches)

    def _load_teams_by_name(self):
        teams = self._team_repository.find_all()

        logger.info("Loaded %d teams", len(teams))

        return {team.name: team for team in teams}

    def _build_matches(
        self,
        commands: list[SyncMatchCommand],
        teams_by_name: dict[str, Team],
    ) -> list[Match]:
        matches: list[Match] = []

        for command in commands:
            if command.start_time is None:
                continue

            home_team = self._get_team_or_throw(teams_by_name, command.home_team_name)
            away_team = self._get_team_or_throw(teams_by_name, command.away_team_name)

            matches.append(
                Match(
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
            )

        return matches

    def _get_team_or_throw(
        self,
        teams_by_name: dict[str, Team],
        team_name: str,
    ) -> Team:
        team = teams_by_name.get(team_name)

        if team is None:
            raise ValueError(f"Team not found: {team_name}")

        return team

    def _save_matches(self, matches: list[Match]) -> None:
        if not matches:
            return

        start = time.perf_counter()

        self._match_repository.save_all(matches)

        elapsed = time.perf_counter() - start

        logger.info("Saved %d matches in %.2fs", len(matches), elapsed)
