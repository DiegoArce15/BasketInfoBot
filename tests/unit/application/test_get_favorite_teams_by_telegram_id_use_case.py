from unittest.mock import Mock

from src.application.get_favorite_teams_by_telegram_id_use_case import (
    GetFavoriteTeamsByTelegramIdUseCase,
)
from src.domain.entities import Team, User
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TELEGRAM_ID_1,
    USER_ID_1,
)


def test_get_favorite_teams_returns_user_favorite_teams(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    mock_user_repo.find_by_telegram_id.return_value = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1),
            User.FavoriteTeam(team_id=TEAM_ID_2),
        ],
    )

    mock_team_repo.find_by_ids.return_value = [
        Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB", country="Spain"),
        Team(id=TEAM_ID_2, name="UCAM Murcia", short_name="UCM", country="Spain"),
    ]

    use_case = GetFavoriteTeamsByTelegramIdUseCase(
        user_repository=mock_user_repo,
        team_repository=mock_team_repo,
    )

    # When
    teams = use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert teams == [
        Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB", country="Spain"),
        Team(id=TEAM_ID_2, name="UCAM Murcia", short_name="UCM", country="Spain"),
    ]

    mock_team_repo.find_by_ids.assert_called_once_with([TEAM_ID_1, TEAM_ID_2])


def test_get_favorite_teams_returns_empty_when_user_does_not_exist(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    mock_user_repo.find_by_telegram_id.return_value = None

    use_case = GetFavoriteTeamsByTelegramIdUseCase(
        user_repository=mock_user_repo,
        team_repository=mock_team_repo,
    )

    # When
    teams = use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert teams == []
    mock_team_repo.find_by_id.assert_not_called()


def test_get_favorite_teams_returns_empty_when_user_has_no_favorites(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    mock_user_repo.find_by_telegram_id.return_value = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[],
    )

    use_case = GetFavoriteTeamsByTelegramIdUseCase(
        user_repository=mock_user_repo,
        team_repository=mock_team_repo,
    )

    # When
    teams = use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert teams == []
    mock_team_repo.find_by_ids.assert_not_called()


def test_get_favorite_teams_ignores_missing_teams(
    mock_user_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    mock_user_repo.find_by_telegram_id.return_value = User(
        id=USER_ID_1,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[
            User.FavoriteTeam(team_id=TEAM_ID_1),
            User.FavoriteTeam(team_id=TEAM_ID_2),
        ],
    )

    mock_team_repo.find_by_ids.return_value = [
        Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB", country="Spain")
    ]

    use_case = GetFavoriteTeamsByTelegramIdUseCase(
        user_repository=mock_user_repo,
        team_repository=mock_team_repo,
    )

    # When
    teams = use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert teams == [
        Team(
            id=TEAM_ID_1,
            name="Real Madrid",
            short_name="RMB",
            country="Spain",
            logo_url=None,
        )
    ]
