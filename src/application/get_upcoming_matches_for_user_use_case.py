
from src.domain.entities import Match, UserId
from src.domain.match_repository import MatchRepository
from src.domain.user_repository import UserRepository


class GetUpcomingMatchesForUserUseCase:
    """Obtiene los próximos partidos de todos los equipos favoritos de un usuario."""

    def __init__(self, user_repo: UserRepository, match_repo: MatchRepository):
        self.user_repo = user_repo
        self.match_repo = match_repo

    def execute(self, user_id: UserId) -> list[Match]:
        user = self.user_repo.find_by_id(user_id)
        if not user or not user.favorite_team_ids:
            return []

        upcoming_matches: list[Match] = []
        for team_id in user.favorite_team_ids:
            matches = self.match_repo.find_upcoming_by_team(team_id)
            upcoming_matches.extend(matches)

        # Evitar duplicados (por si dos equipos favoritos juegan entre sí) y ordenar por fecha
        unique_matches = {match.id.value: match for match in upcoming_matches}.values()
        return sorted(unique_matches, key=lambda m: m.start_time)