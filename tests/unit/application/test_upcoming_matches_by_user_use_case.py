from datetime import UTC, datetime
from unittest.mock import Mock

from src.application.get_upcoming_matches_by_telegram_id_use_case import (
    GetUpcomingMatchesByTelegramIdUseCase,
    MatchResponseDTO,
)
from src.domain.entities import Channel, Match, MatchId, MatchStatus, Team, TeamId, User
from tests.test_utils.constants import (
    TEAM_ID_1,
    TEAM_ID_2,
    TELEGRAM_ID_1,
    TELEGRAM_ID_404,
    USER_ID_1,
    USER_ID_404,
)


def test_get_upcoming_matches_for_user(
    mock_user_repo: Mock, mock_match_repo: Mock, mock_team_repo: Mock
) -> None:
    # Given
    match_date = datetime(2026, 10, 25, 20, 0, tzinfo=UTC)

    # 1. Entidades de dominio que devolverán los mocks
    match = Match(
        id=MatchId("real-madrid-vs-barcelona-2026-10-25"),
        home_team_id=TEAM_ID_1,
        away_team_id=TEAM_ID_2,
        start_time=match_date,
        score=None,
        status=MatchStatus.SCHEDULED,
        channels=[Channel("ESPN")],
        league="ACB",
    )
    home_team = Team(id=TEAM_ID_1, name="Real Madrid", short_name="RMB")
    away_team = Team(id=TEAM_ID_2, name="FC Barcelona", short_name="BAR")

    # 2. Configuración del comportamiento de los mocks
    mock_user_repo.find_by_telegram_id.return_value = User(
        id=USER_ID_1, telegram_id=TELEGRAM_ID_1, username="John Doe", favorite_teams=[]
    )
    mock_match_repo.find_upcoming_by_user.return_value = [match]

    # Simular la búsqueda de equipos por su ID
    def mock_find_team_by_id(team_id: TeamId) -> Team | None:
        teams = {TEAM_ID_1: home_team, TEAM_ID_2: away_team}
        return teams.get(team_id)

    mock_team_repo.find_by_id.side_effect = mock_find_team_by_id

    use_case = GetUpcomingMatchesByTelegramIdUseCase(
        user_repo=mock_user_repo, match_repo=mock_match_repo, team_repo=mock_team_repo
    )

    # When
    result = use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    # 1. Verificamos la estructura y datos de los DTOs retornados
    assert result == [
        MatchResponseDTO(
            home_team_name="Real Madrid",
            away_team_name="FC Barcelona",
            start_time=match_date,
            status="SCHEDULED",
            score=None,
            channels=["ESPN"],
            league="ACB",
        )
    ]

    # 2. Verificamos que se interactuó con los repositorios adecuadamente
    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_match_repo.find_upcoming_by_user.assert_called_once_with(USER_ID_1)
    assert mock_team_repo.find_by_id.call_count == 2


def test_get_upcoming_matches_returns_empty_when_user_does_not_exist(
    mock_user_repo: Mock, mock_match_repo: Mock, mock_team_repo: Mock
) -> None:
    # Given
    mock_user_repo.find_by_telegram_id.return_value = None

    use_case = GetUpcomingMatchesByTelegramIdUseCase(
        user_repo=mock_user_repo, match_repo=mock_match_repo, team_repo=mock_team_repo
    )

    # When
    matches = use_case.execute(telegram_id=TELEGRAM_ID_404)

    # Then
    assert matches == []
    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_404)
    mock_match_repo.find_upcoming_by_user.assert_not_called()
    mock_team_repo.find_by_id.assert_not_called()


def test_get_upcoming_matches_returns_empty_when_user_has_no_favorites(
    mock_user_repo: Mock, mock_match_repo: Mock, mock_team_repo: Mock
) -> None:
    # Given
    mock_user_repo.find_by_telegram_id.return_value = User(
        id=USER_ID_404,
        telegram_id=TELEGRAM_ID_1,
        username="John Doe",
        favorite_teams=[],
    )
    mock_match_repo.find_upcoming_by_user.return_value = []

    use_case = GetUpcomingMatchesByTelegramIdUseCase(
        user_repo=mock_user_repo, match_repo=mock_match_repo, team_repo=mock_team_repo
    )

    # When
    matches = use_case.execute(telegram_id=TELEGRAM_ID_1)

    # Then
    assert matches == []
    mock_user_repo.find_by_telegram_id.assert_called_once_with(TELEGRAM_ID_1)
    mock_match_repo.find_upcoming_by_user.assert_called_once_with(USER_ID_404)
    mock_team_repo.find_by_id.assert_not_called()
