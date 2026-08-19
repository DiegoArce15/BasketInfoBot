from datetime import UTC, datetime
from unittest.mock import MagicMock

from src.application.sync_upcoming_matches_use_case import SyncUpcomingMatchesUseCase
from src.domain.entities import Channel, Match, MatchStatus
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TEAM_ID_3,
    TEAM_ID_4,
)


def test_sync_upcoming_matches_fetches_and_saves_matches():
    # Given
    mock_fetcher = MagicMock()
    mock_repository = MagicMock()

    sample_matches = [
        Match(
            id="real-madrid-vs-barcelona-2026-10-19-20-00",
            home_team_id=TEAM_ID_1,
            away_team_id=TEAM_ID_2,
            start_time=datetime.now(UTC),
            status=MatchStatus.SCHEDULED,
            channels=[Channel(name="Movistar+"), Channel(name="DAZN")],
        ),
        Match(
            id="unicaja-vs-ucam-murcia-2026-10-29-20-00",
            home_team_id=TEAM_ID_3,
            away_team_id=TEAM_ID_4,
            start_time=datetime.now(UTC),
            status=MatchStatus.SCHEDULED,
            channels=[Channel(name="La1")],
        ),
    ]

    mock_fetcher.fetch_upcoming_matches.return_value = sample_matches

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=mock_fetcher,
        match_repository=mock_repository,
    )

    # When
    synced_count = use_case.execute()

    # Then
    mock_fetcher.fetch_upcoming_matches.assert_called_once()

    assert synced_count == 2
    assert mock_repository.save.call_count == 2

    mock_repository.save.assert_any_call(sample_matches[0])
    mock_repository.save.assert_any_call(sample_matches[1])


def test_sync_upcoming_matches_handles_empty_results():
    # Given
    mock_fetcher = MagicMock()
    mock_repository = MagicMock()

    mock_fetcher.fetch_upcoming_matches.return_value = []

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=mock_fetcher,
        match_repository=mock_repository,
    )

    # When
    synced_count = use_case.execute()

    # Then
    mock_fetcher.fetch_upcoming_matches.assert_called_once()
    assert synced_count == 0
    mock_repository.save.assert_not_called()