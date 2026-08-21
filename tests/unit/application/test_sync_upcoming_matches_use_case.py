from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.application.sync_upcoming_matches_use_case import SyncUpcomingMatchesUseCase
from src.domain.entities import Channel, Match, MatchId, MatchStatus, Score, Team
from tests.test_utils.constants import TEAM_ID_1, TEAM_ID_2, TEAM_ID_3, TEAM_ID_4


def test_sync_upcoming_matches_fetches_and_saves_matches():
    # Given
    mock_fetcher = MagicMock()
    mock_match_repository = MagicMock()
    mock_team_repository = MagicMock()

    start_time_1 = datetime(2026, 10, 19, 20, 0, tzinfo=UTC)
    start_time_2 = datetime(2026, 10, 29, 20, 0, tzinfo=UTC)

    real_madrid = Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB")
    barcelona = Team(id=TEAM_ID_2, name="Barça", short_name="BAR")
    unicaja = Team(id=TEAM_ID_3, name="Unicaja", short_name="UNI")
    ucam_murcia = Team(id=TEAM_ID_4, name="UCAM Murcia", short_name="UCM")

    commands = [
        SyncMatchCommand(
            home_team_name="Real Madrid",
            away_team_name="Barça",
            start_time=start_time_1,
            channels=[Channel(name="Movistar+"), Channel(name="DAZN")],
            league="ACB",
            status=MatchStatus.SCHEDULED,
            score=None,
        ),
        SyncMatchCommand(
            home_team_name="Unicaja",
            away_team_name="UCAM Murcia",
            start_time=start_time_2,
            channels=[Channel(name="La1")],
            league="ACB",
            status=MatchStatus.FINISHED,
            score=Score(home=89, away=90),
        ),
    ]

    mock_fetcher.fetch_upcoming_matches.return_value = commands

    mock_team_repository.find_all.return_value = [
        real_madrid,
        barcelona,
        unicaja,
        ucam_murcia,
    ]

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=mock_fetcher,
        match_repository=mock_match_repository,
        team_repository=mock_team_repository,
    )

    # When
    synced_count = use_case.execute()

    # Then
    mock_fetcher.fetch_upcoming_matches.assert_called_once()
    mock_team_repository.find_all.assert_called_once()

    assert synced_count == 2

    mock_match_repository.save_all.assert_called_once_with(
        [
            Match(
                id=MatchId("real-madrid-vs-barca-2026-10-19"),
                home_team_id=TEAM_ID_1,
                away_team_id=TEAM_ID_2,
                start_time=start_time_1,
                channels=[Channel(name="Movistar+"), Channel(name="DAZN")],
                league="ACB",
                status=MatchStatus.SCHEDULED,
                score=None,
            ),
            Match(
                id=MatchId("unicaja-vs-ucam-murcia-2026-10-29"),
                home_team_id=TEAM_ID_3,
                away_team_id=TEAM_ID_4,
                start_time=start_time_2,
                channels=[Channel(name="La1")],
                league="ACB",
                status=MatchStatus.FINISHED,
                score=Score(home=89, away=90),
            ),
        ]
    )

    mock_match_repository.save.assert_not_called()


def test_sync_upcoming_matches_handles_empty_results():
    # Given
    mock_fetcher = MagicMock()
    mock_match_repository = MagicMock()
    mock_team_repository = MagicMock()

    mock_fetcher.fetch_upcoming_matches.return_value = []
    mock_team_repository.find_all.return_value = []

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=mock_fetcher,
        match_repository=mock_match_repository,
        team_repository=mock_team_repository,
    )

    # When
    synced_count = use_case.execute()

    # Then
    mock_fetcher.fetch_upcoming_matches.assert_called_once()
    mock_team_repository.find_all.assert_called_once()

    assert synced_count == 0

    mock_match_repository.save_all.assert_not_called()


def test_sync_upcoming_matches_fails_when_home_team_does_not_exist():
    # Given
    mock_fetcher = MagicMock()
    mock_match_repository = MagicMock()
    mock_team_repository = MagicMock()

    command = SyncMatchCommand(
        home_team_name="Equipo inexistente",
        away_team_name="Real Madrid",
        start_time=datetime(2026, 10, 19, 20, 0, tzinfo=UTC),
        channels=[],
        league="ACB",
        status=MatchStatus.SCHEDULED,
        score=None,
    )

    real_madrid = Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB")

    mock_fetcher.fetch_upcoming_matches.return_value = [command]
    mock_team_repository.find_all.return_value = [real_madrid]

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=mock_fetcher,
        match_repository=mock_match_repository,
        team_repository=mock_team_repository,
    )

    # When / Then
    with pytest.raises(
        ValueError,
        match="Equipo local no encontrado: Equipo inexistente",
    ):
        use_case.execute()

    mock_team_repository.find_all.assert_called_once()

    mock_match_repository.save_all.assert_not_called()
    mock_match_repository.save.assert_not_called()


def test_sync_upcoming_matches_fails_when_away_team_does_not_exist():
    # Given
    mock_fetcher = MagicMock()
    mock_match_repository = MagicMock()
    mock_team_repository = MagicMock()

    real_madrid = Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB")

    command = SyncMatchCommand(
        home_team_name="Real Madrid",
        away_team_name="Equipo inexistente",
        start_time=datetime(2026, 10, 19, 20, 0, tzinfo=UTC),
        channels=[],
        league="ACB",
        status=MatchStatus.SCHEDULED,
        score=None,
    )

    mock_fetcher.fetch_upcoming_matches.return_value = [command]
    mock_team_repository.find_all.return_value = [real_madrid]

    use_case = SyncUpcomingMatchesUseCase(
        match_fetcher=mock_fetcher,
        match_repository=mock_match_repository,
        team_repository=mock_team_repository,
    )

    # When / Then
    with pytest.raises(
        ValueError,
        match="Equipo visitante no encontrado: Equipo inexistente",
    ):
        use_case.execute()

    mock_team_repository.find_all.assert_called_once()

    mock_match_repository.save_all.assert_not_called()
    mock_match_repository.save.assert_not_called()
