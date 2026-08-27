from unittest.mock import Mock

import pytest

from src.application.add_favorite_team_by_telegram_id_use_case import (
    AddFavoriteTeamByTelegramIdUseCase,
)
from src.domain.team import Team
from src.domain.user import User
from src.shared.application.application_error import ApplicationError
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_404,
    TELEGRAM_ID_1,
    TELEGRAM_ID_404,
    USER_ID_1,
)
from tests.test_utils.team_mother import a_team
from tests.test_utils.user_mother import an_user


def test_add_favorite_team_should_be_ok(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = AddFavoriteTeamTestFixture(mock_user_repo, mock_team_repo)

    fixture.given_user_repository_returns(
        User(
            id=USER_ID_1,
            telegram_id=TELEGRAM_ID_1,
            username="John Doe",
            favorite_teams=[],
        )
    )
    fixture.given_team_repository_returns(a_team(id=TEAM_ID_1))

    # When
    fixture.use_case.execute(telegram_id=TELEGRAM_ID_1, team_id=TEAM_ID_1)

    # Then
    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_1)
    mock_user_repo.save.assert_called_once_with(
        User(
            id=USER_ID_1,
            telegram_id=TELEGRAM_ID_1,
            username="John Doe",
            favorite_teams=[User.FavoriteTeam(TEAM_ID_1, notifications_enabled=True)],
        )
    )


def test_add_favorite_team_does_nothing_when_team_is_already_favorite(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = AddFavoriteTeamTestFixture(mock_user_repo, mock_team_repo)

    fixture.given_user_repository_returns(an_user(favorite_teams=[TEAM_ID_1]))
    fixture.given_team_repository_returns(a_team(id=TEAM_ID_1))

    # When
    fixture.use_case.execute(telegram_id=TELEGRAM_ID_1, team_id=TEAM_ID_1)

    # Then
    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_1)
    mock_user_repo.save.assert_not_called()


def test_add_favorite_team_fails_when_user_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = AddFavoriteTeamTestFixture(mock_user_repo, mock_team_repo)

    fixture.given_user_repository_returns(None)

    # When / Then
    with pytest.raises(
        ApplicationError,
        match="User with telegram id 404 not found",
    ):
        fixture.use_case.execute(telegram_id=TELEGRAM_ID_404, team_id=TEAM_ID_1)

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_404)
    mock_team_repo.find_by_id.assert_not_called()
    mock_user_repo.save.assert_not_called()


def test_add_favorite_team_fails_when_team_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = AddFavoriteTeamTestFixture(mock_user_repo, mock_team_repo)

    fixture.given_user_repository_returns(an_user(favorite_teams=[]))
    fixture.given_team_repository_returns(None)

    # When / Then
    with pytest.raises(
        ApplicationError,
        match="Team 00000000-0000-0000-0000-000000000404 not found",
    ):
        fixture.use_case.execute(telegram_id=TELEGRAM_ID_1, team_id=TEAM_ID_404)

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_404)
    mock_user_repo.save.assert_not_called()


class AddFavoriteTeamTestFixture:
    def __init__(
        self,
        user_repo: Mock,
        team_repo: Mock,
    ) -> None:
        self.user_repo = user_repo
        self.team_repo = team_repo

        self.use_case = AddFavoriteTeamByTelegramIdUseCase(
            user_repo=self.user_repo, team_repo=self.team_repo
        )

    def given_user_repository_returns(self, user: User | None) -> None:
        self.user_repo.find_by_telegram_id.return_value = user

    def given_team_repository_returns(self, team: Team | None) -> None:
        self.team_repo.find_by_id.return_value = team
