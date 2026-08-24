from datetime import UTC, datetime
from unittest.mock import Mock

from src.application.get_upcoming_matches_by_telegram_id_use_case import (
    GetUpcomingMatchesByTelegramIdUseCase,
    MatchResponseDTO,
)
from src.domain.entities import (
    Channel,
    Match,
    MatchId,
    MatchStatus,
    Score,
    Team,
    User,
)
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TEAM_ID_404,
    TELEGRAM_ID_1,
    TELEGRAM_ID_404,
    USER_ID_1,
)
from tests.test_utils.match_mother import a_match
from tests.test_utils.team_mother import a_team
from tests.test_utils.user_mother import an_user


def test_get_upcoming_matches_for_user(
    mock_user_repo: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = GetUpcomingMatchesByTelegramIdTestFixture(
        mock_user_repo,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(
        an_user(id=USER_ID_1, favorite_teams=[TEAM_ID_1])
    )
    fixture.given_match_repository_returns(
        [
            Match(
                id=MatchId("real-madrid-vs-barcelona-2026-10-25"),
                home_team_id=TEAM_ID_1,
                away_team_id=TEAM_ID_2,
                start_time=datetime(2026, 10, 25, 20, 0, tzinfo=UTC),
                score=None,
                status=MatchStatus.SCHEDULED,
                channels=[Channel("ESPN")],
                league="ACB",
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
    result = fixture.use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert result == [
        MatchResponseDTO(
            home_team_name="Real Madrid",
            away_team_name="Barça",
            start_time=datetime(2026, 10, 25, 20, 0, tzinfo=UTC),
            status="SCHEDULED",
            score=None,
            channels=["ESPN"],
            league="ACB",
        )
    ]

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_match_repo.find_upcoming_by_user.assert_called_once_with(USER_ID_1)
    mock_team_repo.find_all.assert_called_once()


def test_get_upcoming_matches_returns_empty_when_user_does_not_exist(
    mock_user_repo: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = GetUpcomingMatchesByTelegramIdTestFixture(
        mock_user_repo,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(None)

    # When
    result = fixture.use_case.execute(telegram_id=TELEGRAM_ID_404)

    # Then
    assert result == []

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_404)
    mock_match_repo.find_upcoming_by_user.assert_not_called()
    mock_team_repo.find_all.assert_not_called()


def test_get_upcoming_matches_returns_empty_when_user_has_no_favorite_teams(
    mock_user_repo: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = GetUpcomingMatchesByTelegramIdTestFixture(
        mock_user_repo,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(an_user(favorite_teams=[]))

    # When
    result = fixture.use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert result == []

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_match_repo.find_upcoming_by_user.assert_not_called()
    mock_team_repo.find_all.assert_not_called()


def test_get_upcoming_matches_returns_empty_when_no_matches_are_found(
    mock_user_repo: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = GetUpcomingMatchesByTelegramIdTestFixture(
        mock_user_repo,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(
        an_user(id=USER_ID_1, favorite_teams=[TEAM_ID_1])
    )
    fixture.given_match_repository_returns([])

    # When
    result = fixture.use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert result == []

    mock_match_repo.find_upcoming_by_user.assert_called_once_with(USER_ID_1)
    mock_team_repo.find_all.assert_not_called()


def test_get_upcoming_matches_returns_match_score(
    mock_user_repo: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = GetUpcomingMatchesByTelegramIdTestFixture(
        mock_user_repo,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(an_user(favorite_teams=[TEAM_ID_1]))
    fixture.given_match_repository_returns(
        [
            Match(
                id=MatchId("real-madrid-vs-barcelona-2026-10-25"),
                home_team_id=TEAM_ID_1,
                away_team_id=TEAM_ID_2,
                start_time=datetime(2026, 10, 25, 20, 0, tzinfo=UTC),
                score=Score(home=89, away=90),
                status=MatchStatus.FINISHED,
                channels=[Channel("ESPN")],
                league="ACB",
            )
        ]
    )
    fixture.given_team_repository_returns(
        [
            a_team(id=TEAM_ID_1, name="Real Madrid"),
            a_team(id=TEAM_ID_2, name="FC Barcelona"),
        ]
    )

    # When
    result = fixture.use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert result[0].score == "89 - 90"


def test_get_upcoming_matches_ignores_match_when_team_does_not_exist(
    mock_user_repo: Mock,
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = GetUpcomingMatchesByTelegramIdTestFixture(
        mock_user_repo,
        mock_match_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(an_user(favorite_teams=[TEAM_ID_1]))
    fixture.given_match_repository_returns(
        [a_match(home_team_id=TEAM_ID_1, away_team_id=TEAM_ID_404)]
    )
    fixture.given_team_repository_returns([a_team(id=TEAM_ID_1)])

    # When
    result = fixture.use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert result == []


class GetUpcomingMatchesByTelegramIdTestFixture:
    def __init__(
        self,
        user_repo: Mock,
        match_repo: Mock,
        team_repo: Mock,
    ) -> None:
        self.user_repo = user_repo
        self.match_repo = match_repo
        self.team_repo = team_repo

        self.use_case = GetUpcomingMatchesByTelegramIdUseCase(
            user_repo=self.user_repo,
            match_repo=self.match_repo,
            team_repo=self.team_repo,
        )

    def given_user_repository_returns(self, user: User | None) -> None:
        self.user_repo.find_by_telegram_id.return_value = user

    def given_match_repository_returns(self, matches: list[Match]) -> None:
        self.match_repo.find_upcoming_by_user.return_value = matches

    def given_team_repository_returns(self, teams: list[Team]) -> None:
        self.team_repo.find_all.return_value = teams
