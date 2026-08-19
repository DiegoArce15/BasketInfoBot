from unittest.mock import Mock

import pytest

from src.application.add_favorite_team_use_case import AddFavoriteTeamUseCase
from src.domain.entities import Team, User
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_404,
    TELEGRAM_ID_1,
    USER_ID_1,
    USER_ID_404,
)


def test_add_favorite_team_should_be_ok(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=USER_ID_1, telegram_id=TELEGRAM_ID_1, username="John Doe", favorite_teams=[]
    )
    mock_team_repo.find_by_id.return_value = Team(id=TEAM_ID_1, name="Real Madrid")

    use_case = AddFavoriteTeamUseCase(
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
    mock_user_repo.save.assert_called_once()


def test_add_favorite_team_fails_when_user_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = None

    use_case = AddFavoriteTeamUseCase(
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


def test_add_favorite_team_fails_when_team_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=USER_ID_1, telegram_id=TELEGRAM_ID_1, username="John Doe", favorite_teams=[]
    )
    mock_team_repo.find_by_id.return_value = None

    use_case = AddFavoriteTeamUseCase(
        mock_user_repo,
        mock_team_repo,
    )

    # When / Then
    with pytest.raises(
        ValueError, match="El equipo 00000000-0000-0000-0000-000000000404 no existe"
    ):
        use_case.execute(
            user_id=USER_ID_1,
            team_id=TEAM_ID_404,
        )

    mock_user_repo.find_by_id.assert_called_once_with(USER_ID_1)
    mock_team_repo.find_by_id.assert_called_once_with(TEAM_ID_404)
