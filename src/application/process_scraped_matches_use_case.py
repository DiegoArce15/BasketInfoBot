
from src.domain.entities import Match
from src.domain.match_repository import MatchRepository
from src.domain.team_repository import TeamRepository


class ProcessScrapedMatchesUseCase:
    """Procesa y persiste la lista de partidos y equipos extraídos del scraper."""

    def __init__(self, team_repo: TeamRepository, match_repo: MatchRepository):
        self.team_repo = team_repo
        self.match_repo = match_repo

    def execute(self, scraped_matches: list[Match]) -> None:
        for match in scraped_matches:
            self.team_repo.save(match.home_team)
            self.team_repo.save(match.away_team)

            self.match_repo.save(match)