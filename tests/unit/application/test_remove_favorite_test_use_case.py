from unittest.mock import Mock

import pytest

from src.application.remove_favorite_team_use_case import RemoveFavoriteTeamUseCase
from src.domain.entities import TeamId, User, UserId


def test_remove_favorite_team_success(
    mock_user_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=UserId(1), username="John Doe", favorite_team_ids=[TeamId("real-madrid")]
    )

    use_case = RemoveFavoriteTeamUseCase(
        mock_user_repo,
    )

    # When
    use_case.execute(
        user_id=UserId(1),
        team_id=TeamId("real-madrid"),
    )

    # Then
    mock_user_repo.find_by_id.assert_called_once_with(UserId(1))
    mock_user_repo.save.assert_called_once_with(
        User(
            id=UserId(1),
            username="John Doe",
            favorite_team_ids=[],
        )
    )


def test_remove_favorite_team_fails_when_user_does_not_exist(
    mock_user_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = None

    use_case = RemoveFavoriteTeamUseCase(
        mock_user_repo,
    )

    # When / Then
    with pytest.raises(
        ValueError,
        match="Usuario con id 404 no encontrado",
    ):
        use_case.execute(
            user_id=UserId(404),
            team_id=TeamId("real-madrid"),
        )

    mock_user_repo.find_by_id.assert_called_once_with(UserId(404))
