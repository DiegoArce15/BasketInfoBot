import os
import sys

from src.application.sync_upcoming_matches_use_case import (
    SyncUpcomingMatchesUseCase,
)
from src.infrastructure.out.persistence.postgres_match_persistence import (
    PostgresMatchPersistence,
)
from src.infrastructure.out.scrapers.acb_scraper import AcbScraper


def main() -> None:
    print("Iniciando sincronización de próximos partidos...")

    database_url = os.environ["DATABASE_URL"]

    match_fetcher = AcbScraper()
    match_repository = PostgresMatchPersistence(database_url)

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=match_fetcher,
        match_repository=match_repository,
    )

    try:
        matches_count = use_case.execute()
    except Exception as exc:
        print(
            f"Error durante la sincronización: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"Sincronización completada con éxito. "
        f"{matches_count} partidos procesados."
    )


if __name__ == "__main__":
    main()