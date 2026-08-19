from domain.match_fetcher import MatchFetcher
from domain.match_repository import MatchRepository


class SyncUpcomingMatchesUseCase:
    def __init__(self, match_fetcher: MatchFetcher, match_repository: MatchRepository):
        self._match_fetcher = match_fetcher
        self._match_repository = match_repository

    def execute(self) -> int:
        # 1. Obtener partidos frescos del scraper
        fetched_matches = self._match_fetcher.fetch_upcoming_matches()

        # 2. Guardar o actualizar cada partido en la base de datos
        for match in fetched_matches:
            self._match_repository.save(match)

        return len(fetched_matches)
