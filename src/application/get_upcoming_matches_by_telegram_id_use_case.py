import logging
from dataclasses import dataclass
from datetime import datetime

from src.domain.match import Match
from src.domain.match_repository import MatchRepository
from src.domain.team import Team, TeamId
from src.domain.team_repository import TeamRepository
from src.domain.user import TelegramId
from src.domain.user_repository import UserRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MatchResponseDTO:
    home_team_name: str
    away_team_name: str
    start_time: datetime
    status: str
    channels: list[str] | None = None
    league: str | None = None
    score: str | None = None


class GetUpcomingMatchesByTelegramIdUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        match_repo: MatchRepository,
        team_repo: TeamRepository,
    ) -> None:
        self._user_repo = user_repo
        self._match_repo = match_repo
        self._team_repo = team_repo

    def execute(self, telegram_id: TelegramId) -> list[MatchResponseDTO]:
        logger.info(
            "Get upcoming matches for user with telegram_id=%s", telegram_id.value
        )
        user = self._user_repo.find_by_telegram_id(telegram_id)

        if user is None:
            logger.warning("User with telegram id %s not found", telegram_id.value)
            return []

        if not user.favorite_teams:
            logger.debug(
                "User with telegram id %s has no favorite teams", telegram_id.value
            )
            return []

        matches = self._match_repo.find_upcoming_by_user(user.id)

        if not matches:
            logger.debug(
                "No upcoming matches found for user with telegram id %s",
                telegram_id.value,
            )
            return []

        teams_by_id = self._get_all_teams_by_id()

        return self._build_match_responses(matches, teams_by_id)

    def _get_all_teams_by_id(self) -> dict[TeamId, Team]:
        teams = self._team_repo.find_all()

        return {team.id: team for team in teams}

    def _build_match_responses(
        self,
        matches: list[Match],
        teams_by_id: dict[TeamId, Team],
    ) -> list[MatchResponseDTO]:
        responses = []

        for match in matches:
            response = self._build_match_response(match, teams_by_id)

            if response is not None:
                responses.append(response)

        return responses

    def _build_match_response(
        self,
        match: Match,
        teams_by_id: dict[TeamId, Team],
    ) -> MatchResponseDTO | None:
        home_team = teams_by_id.get(match.home_team_id)
        away_team = teams_by_id.get(match.away_team_id)

        if home_team is None or away_team is None:
            logger.warning(
                "Could not build response for match %s: team not found",
                match.id.value,
            )
            return None

        score = None
        if match.score is not None:
            score = f"{match.score.home} - {match.score.away}"

        return MatchResponseDTO(
            home_team_name=home_team.name,
            away_team_name=away_team.name,
            start_time=match.start_time,
            status=match.status.value,
            channels=[channel.name for channel in match.channels],
            league=match.league,
            score=score,
        )
