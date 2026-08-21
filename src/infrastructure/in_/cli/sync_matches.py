import sys

from src.application.sync_upcoming_matches_use_case import SyncUpcomingMatchesUseCase
from src.infrastructure.out.persistence.postgres_match_persistence import (
    PostgresMatchPersistence,
)
from src.infrastructure.out.persistence.postgres_team_persistence import (
    PostgresTeamPersistence,
)
from src.infrastructure.out.scrapers.acb_scraper import AcbScraper
from src.shared.infrastructure.config.settings import Settings


def main() -> None:
    print("Iniciando sincronización de próximos partidos...")

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
        print("Ejecutando sincronización...")
        matches_count = use_case.execute()
        print("Use case terminado.")
    # ruff: noqa: BLE001
    except Exception as exc:
        print(f"Error durante la sincronización: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Sincronización completada con éxito. {matches_count} partidos procesados.")


if __name__ == "__main__":
    main()
