from unittest.mock import Mock

import pytest

from src.application.add_favorite_team_use_case import AddFavoriteTeamUseCase
from src.domain.entities import Team, TeamId, User, UserId


def test_add_favorite_team_should_be_ok(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=UserId(1), username="John Doe", favorite_team_ids=[]
    )
    mock_team_repo.find_by_id.return_value = Team(
        id=TeamId("real-madrid"), name="Real Madrid"
    )

    use_case = AddFavoriteTeamUseCase(
        mock_user_repo,
        mock_team_repo,
    )

    # When
    use_case.execute(
        user_id=UserId(1),
        team_id=TeamId("real-madrid"),
    )

    # Then
    mock_user_repo.find_by_id.assert_called_once_with(UserId(1))
    mock_team_repo.find_by_id.assert_called_once_with(TeamId("real-madrid"))
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
        match="Usuario con id 404 no encontrado",
    ):
        use_case.execute(
            user_id=UserId(404),
            team_id=TeamId("real-madrid"),
        )

    mock_user_repo.find_by_id.assert_called_once_with(UserId(404))


def test_add_favorite_team_fails_when_team_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
):
    # Given
    mock_user_repo.find_by_id.return_value = User(
        id=UserId(1), username="John Doe", favorite_team_ids=[]
    )
    mock_team_repo.find_by_id.return_value = None

    use_case = AddFavoriteTeamUseCase(
        mock_user_repo,
        mock_team_repo,
    )

    # When / Then
    with pytest.raises(ValueError, match="El equipo real-madrid no existe"):
        use_case.execute(
            user_id=UserId(1),
            team_id=TeamId("real-madrid"),
        )

    mock_user_repo.find_by_id.assert_called_once_with(UserId(1))
    mock_team_repo.find_by_id.assert_called_once_with(TeamId("real-madrid"))
