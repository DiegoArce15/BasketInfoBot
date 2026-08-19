from unittest.mock import Mock

from src.application.get_available_teams_use_case import GetAvailableTeamsUseCase
from src.domain.entities import Team
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
)


def test_get_available_teams_returns_all_stored_teams(
    mock_team_repo: Mock,
):
    # Given
    real_madrid = Team(
        id=TEAM_ID_1,
        name="Real Madrid",
    )
    valencia = Team(
        id=TEAM_ID_2,
        name="Valencia Basket",
    )

    mock_team_repo.find_all.return_value = [
        real_madrid,
        valencia,
    ]

    use_case = GetAvailableTeamsUseCase(
        mock_team_repo,
    )

    # When
    result = use_case.execute()

    # Then
    assert result == [
        real_madrid,
        valencia,
    ]

    mock_team_repo.find_all.assert_called_once_with()
