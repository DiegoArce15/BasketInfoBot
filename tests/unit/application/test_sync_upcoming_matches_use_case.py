from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.application.sync_upcoming_matches_command import SyncMatchCommand
from src.application.sync_upcoming_matches_use_case import SyncUpcomingMatchesUseCase
from src.domain.match import Channel, Match, MatchId, MatchStatus, Score
from src.domain.team import Team
from src.shared.application.application_error import ApplicationError
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TEAM_ID_3,
    TEAM_ID_4,
)
from tests.test_utils.team_mother import a_team


def test_sync_upcoming_matches_fetches_and_saves_matches(
    mock_match_fetcher: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = SyncUpcomingMatchesTestFixture(
        mock_match_fetcher,
        mock_match_repo,
        mock_team_repo,
    )

    start_time_1 = datetime(2026, 10, 19, 20, 0, tzinfo=UTC)
    start_time_2 = datetime(2026, 10, 29, 20, 0, tzinfo=UTC)

    fixture.given_match_fetcher_returns(
        [
            SyncMatchCommand(
                home_team_name="Real Madrid",
                away_team_name="Barça",
                start_time=start_time_1,
                channels=[
                    Channel(name="Movistar+"),
                    Channel(name="DAZN"),
                ],
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
    )

    fixture.given_team_repository_returns(
        [
            a_team(id=TEAM_ID_1, name="Real Madrid"),
            a_team(id=TEAM_ID_2, name="Barça"),
            a_team(id=TEAM_ID_3, name="Unicaja"),
            a_team(id=TEAM_ID_4, name="UCAM Murcia"),
        ]
    )

    # When
    synced_count = fixture.use_case.execute()

    # Then
    assert synced_count == 2

    mock_match_fetcher.fetch_upcoming_matches.assert_called_once()
    mock_team_repo.find_all.assert_called_once()

    mock_match_repo.save_all.assert_called_once_with(
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


def test_sync_upcoming_matches_returns_zero_when_no_matches_are_found(
    mock_match_fetcher: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = SyncUpcomingMatchesTestFixture(
        mock_match_fetcher,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_match_fetcher_returns([])
    fixture.given_team_repository_returns([])

    # When
    synced_count = fixture.use_case.execute()

    # Then
    assert synced_count == 0

    mock_match_fetcher.fetch_upcoming_matches.assert_called_once()
    mock_team_repo.find_all.assert_called_once()
    mock_match_repo.save_all.assert_not_called()


def test_sync_upcoming_matches_ignores_matches_without_start_time(
    mock_match_fetcher: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = SyncUpcomingMatchesTestFixture(
        mock_match_fetcher,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_match_fetcher_returns(
        [
            SyncMatchCommand(
                home_team_name="Real Madrid",
                away_team_name="Barça",
                start_time=None,
                channels=[],
                league="ACB",
                status=MatchStatus.SCHEDULED,
                score=None,
            )
        ]
    )
    fixture.given_team_repository_returns(
        [
            a_team(id=TEAM_ID_1, name="Real Madrid"),
            a_team(id=TEAM_ID_2, name="Barça"),
        ]
    )

    # When
    synced_count = fixture.use_case.execute()

    # Then
    assert synced_count == 0

    mock_match_repo.save_all.assert_not_called()


def test_sync_upcoming_matches_fails_when_team_does_not_exist(
    mock_match_fetcher: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = SyncUpcomingMatchesTestFixture(
        mock_match_fetcher,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_match_fetcher_returns(
        [
            SyncMatchCommand(
                home_team_name="Unknown Team",
                away_team_name="Real Madrid",
                start_time=datetime(2026, 10, 19, 20, 0, tzinfo=UTC),
                channels=[],
                league="ACB",
                status=MatchStatus.SCHEDULED,
                score=None,
            )
        ]
    )
    fixture.given_team_repository_returns(
        [
            a_team(id=TEAM_ID_1, name="Real Madrid"),
        ]
    )

    # When / Then
    with pytest.raises(
        ApplicationError,
        match="Team not found: Unknown Team",
    ):
        fixture.use_case.execute()

    mock_team_repo.find_all.assert_called_once()
    mock_match_repo.save_all.assert_not_called()


class SyncUpcomingMatchesTestFixture:
    def __init__(
        self,
        match_fetcher: Mock,
        match_repository: Mock,
        team_repository: Mock,
    ) -> None:
        self.match_fetcher = match_fetcher
        self.match_repository = match_repository
        self.team_repository = team_repository

        self.use_case = SyncUpcomingMatchesUseCase(
            match_fetcher=self.match_fetcher,
            match_repository=self.match_repository,
            team_repository=self.team_repository,
        )

    def given_match_fetcher_returns(
        self,
        commands: list[SyncMatchCommand],
    ) -> None:
        self.match_fetcher.fetch_upcoming_matches.return_value = commands

    def given_team_repository_returns(
        self,
        teams: list[Team],
    ) -> None:
        self.team_repository.find_all.return_value = teams
