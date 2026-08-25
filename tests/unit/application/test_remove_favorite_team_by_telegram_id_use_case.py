from unittest.mock import Mock

import pytest

from src.application.remove_favorite_team_by_telegram_id_use_case import (
    RemoveFavoriteTeamByTelegramIdUseCase,
)
from src.domain.entities import Team, User
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TEAM_ID_404,
    TELEGRAM_ID_1,
    TELEGRAM_ID_404,
    USER_ID_1,
)
from tests.test_utils.team_mother import a_team
from tests.test_utils.user_mother import an_user


def test_remove_favorite_team_success(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = RemoveFavoriteTeamTestFixture(
        mock_user_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(
        an_user(
            id=USER_ID_1,
            favorite_teams=[TEAM_ID_1],
        )
    )
    fixture.given_team_repository_returns(a_team(id=TEAM_ID_1))

    # When
    fixture.use_case.execute(
        telegram_id=TELEGRAM_ID_1,
        team_id=TEAM_ID_1,
    )

    # Then
    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_1)
    mock_user_repo.save.assert_called_once()


def test_remove_favorite_team_does_not_save_when_team_is_not_a_favorite_one(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = RemoveFavoriteTeamTestFixture(
        mock_user_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(
        an_user(
            favorite_teams=[TEAM_ID_1],
        )
    )
    fixture.given_team_repository_returns(a_team(id=TEAM_ID_2))

    # When
    fixture.use_case.execute(
        telegram_id=TELEGRAM_ID_1,
        team_id=TEAM_ID_2,
    )

    # Then
    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_2)
    mock_user_repo.save.assert_not_called()


def test_remove_favorite_team_fails_when_user_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = RemoveFavoriteTeamTestFixture(
        mock_user_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(None)

    # When / Then
    with pytest.raises(
        ValueError,
        match="User with telegram id 404 not found",
    ):
        fixture.use_case.execute(
            telegram_id=TELEGRAM_ID_404,
            team_id=TEAM_ID_1,
        )

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_404)
    mock_team_repo.find_by_id.assert_not_called()
    mock_user_repo.save.assert_not_called()


def test_remove_favorite_team_fails_when_team_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    fixture = RemoveFavoriteTeamTestFixture(
        mock_user_repo,
        mock_team_repo,
    )

    fixture.given_user_repository_returns(
        an_user(
            favorite_teams=[TEAM_ID_1],
        )
    )
    fixture.given_team_repository_returns(None)

    # When / Then
    with pytest.raises(
        ValueError,
        match="Team 00000000-0000-0000-0000-000000000404 not found",
    ):
        fixture.use_case.execute(
            telegram_id=TELEGRAM_ID_1,
            team_id=TEAM_ID_404,
        )

    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_404)
    mock_user_repo.save.assert_not_called()


class RemoveFavoriteTeamTestFixture:
    def __init__(
        self,
        user_repo: Mock,
        team_repo: Mock,
    ) -> None:
        self.user_repo = user_repo
        self.team_repo = team_repo

        self.use_case = RemoveFavoriteTeamByTelegramIdUseCase(
            user_repo=self.user_repo,
            team_repo=self.team_repo,
        )

    def given_user_repository_returns(self, user: User | None) -> None:
        self.user_repo.find_by_telegram_id.return_value = user

    def given_team_repository_returns(self, team: Team | None) -> None:
        self.team_repo.find_by_id.return_value = team
