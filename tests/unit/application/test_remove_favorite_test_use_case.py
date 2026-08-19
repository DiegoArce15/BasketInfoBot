from unittest.mock import Mock

import pytest

from src.application.remove_favorite_team_use_case import RemoveFavoriteTeamUseCase
from src.domain.entities import Team, User
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TEAM_ID_404,
    TELEGRAM_ID_1,
    USER_ID_1,
    USER_ID_404,
)


def test_remove_favorite_team_success(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True),
        ],
    )
    mock_team_repo.find_by_id.return_value = Team(
        id=TEAM_ID_1,
        name="Real Madrid",
        country="Spain",
        logo_url="http:fake.s3/real-madrid.png",
    )

    use_case = RemoveFavoriteTeamUseCase(
        mock_user_repo,
        mock_team_repo,
    )

    # When
    use_case.execute(
        user_id=USER_ID_1,
        team_id=TEAM_ID_1,
    )

    # Then
    mock_user_repo.find_by_id.assert_called_once_with(USER_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_1)
    mock_user_repo.save.assert_called_once_with(
        User(
            id=USER_ID_1,
            telegram_id=TELEGRAM_ID_1,
            username="John Doe",
            favorite_teams=[],
        )
    )


def test_remove_favorite_team_does_not_remove_anything_when_team_is_not_a_favorite_one(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True),
        ],
    )
    mock_team_repo.find_by_id.return_value = Team(
        id=TEAM_ID_2,
        name="UCAM Murcia",
        country="Spain",
        logo_url="http:fake.s3/ucam-murcia.png",
    )

    use_case = RemoveFavoriteTeamUseCase(
        mock_user_repo,
        mock_team_repo,
    )

    # When
    use_case.execute(
        user_id=USER_ID_1,
        team_id=TEAM_ID_2,
    )

    # Then
    mock_user_repo.find_by_id.assert_called_once_with(USER_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_2)
    mock_user_repo.save.assert_not_called()


def test_remove_favorite_team_fails_when_user_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = None

    use_case = RemoveFavoriteTeamUseCase(
        mock_user_repo,
        mock_team_repo,
    )

    # When / Then
    with pytest.raises(
        ValueError,
        match="Usuario con id 00000000-0000-0000-0000-000000000404 no encontrado",
    ):
        use_case.execute(
            user_id=USER_ID_404,
            team_id=TEAM_ID_1,
        )

    mock_user_repo.find_by_id.assert_called_once_with(USER_ID_404)
    mock_team_repo.find_by_id.assert_not_called()
    mock_user_repo.save.assert_not_called()


def test_remove_favorite_team_fails_when_team_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1, notifications_enabled=True),
        ],
    )
    mock_team_repo.find_by_id.return_value = None

    use_case = RemoveFavoriteTeamUseCase(
        mock_user_repo,
        mock_team_repo,
    )

    # When / Then
    with pytest.raises(
        ValueError,
        match="Equipo con id 00000000-0000-0000-0000-000000000404 no encontrado",
    ):
        use_case.execute(
            user_id=USER_ID_1,
            team_id=TEAM_ID_404,
        )

    mock_user_repo.find_by_id.assert_called_once_with(USER_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_404)
    mock_user_repo.save.assert_not_called()
