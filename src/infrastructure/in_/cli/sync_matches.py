import logging
import sys

from src.application.sync_upcoming_matches_use_case import SyncUpcomingMatchesUseCase
from src.infrastructure.out.persistence.postgres_match_persistence import (
    PostgresMatchPersistence,
)
from src.infrastructure.out.persistence.postgres_team_persistence import (
    PostgresTeamPersistence,
)
from src.infrastructure.out.scrapers.acb_scraper import AcbScraper
from src.shared.infrastructure.config.logging_config import configure_logging
from src.shared.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()

    logger.info("Starting upcoming matches synchronization")

    settings = Settings()

    match_fetcher = AcbScraper(target_url=settings.acb_target_url)
    match_repository = PostgresMatchPersistence(settings.database_url)
    team_repository = PostgresTeamPersistence(settings.database_url)

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=match_fetcher,
        match_repository=match_repository,
        team_repository=team_repository,
    )

    try:
        matches_count = use_case.execute()
    except Exception:
        logger.exception("Upcoming matches synchronization failed")
        sys.exit(1)

    logger.info(
        "Upcoming matches synchronization completed successfully: %d matches processed",
        matches_count,
    )


if __name__ == "__main__":
    main()
