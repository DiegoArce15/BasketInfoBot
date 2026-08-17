from datetime import UTC, datetime
from unittest.mock import Mock

from src.application.get_upcoming_matches_by_user_use_case import (
    GetUpcomingMatchesByUserUseCase,
    MatchResponseDTO,
)
from src.domain.entities import Match, MatchId, MatchStatus, Team, TeamId, UserId


def test_get_upcoming_matches_for_user(
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    user_id = UserId(123)
    match_date = datetime(2026, 10, 25, 20, 0, tzinfo=UTC)

    # 1. Entidades de dominio que devolverán los mocks
    match = Match(
        id=MatchId("real-madrid-vs-barcelona-2026-10-25"),
        home_team_id=TeamId("real-madrid"),
        away_team_id=TeamId("barcelona"),
        start_time=match_date,
        score=None,
        status=MatchStatus.SCHEDULED,
        channel="ESPN",
        league="ACB",
    )
    home_team = Team(id=TeamId("real-madrid"), name="Real Madrid")
    away_team = Team(id=TeamId("barcelona"), name="FC Barcelona")

    # 2. Configuración del comportamiento de los mocks
    mock_match_repo.find_upcoming_by_user.return_value = [match]

    # Simular la búsqueda de equipos por su ID
    def mock_find_team_by_id(team_id: TeamId) -> Team | None:
        teams = {TeamId("real-madrid"): home_team, TeamId("barcelona"): away_team}
        return teams.get(team_id)

    mock_team_repo.find_by_id.side_effect = mock_find_team_by_id

    use_case = GetUpcomingMatchesByUserUseCase(
        match_repository=mock_match_repo,
        team_repository=mock_team_repo,
    )

    # When
    result = use_case.execute(user_id=user_id)

    # Then
    # 1. Verificamos la estructura y datos de los DTOs retornados
    assert len(result) == 1
    dto = result[0]
    assert isinstance(dto, MatchResponseDTO)
    assert dto.home_team_name == "Real Madrid"
    assert dto.away_team_name == "FC Barcelona"
    assert dto.start_time == match_date
    assert dto.status == "SCHEDULED"
    assert dto.score is None
    assert dto.channel == "ESPN"
    assert dto.league == "ACB"

    # 2. Verificamos que se interactuó con los repositorios adecuadamente
    mock_match_repo.find_upcoming_by_user.assert_called_once_with(user_id)
    assert mock_team_repo.find_by_id.call_count == 2


def test_get_upcoming_matches_returns_empty_when_user_has_no_favorites(
    mock_match_repo: Mock,
    mock_team_repo: Mock,
) -> None:
    # Given
    mock_match_repo.find_upcoming_by_user.return_value = []

    use_case = GetUpcomingMatchesByUserUseCase(
        match_repository=mock_match_repo,
        team_repository=mock_team_repo,
    )

    # When
    matches = use_case.execute(user_id=UserId(404))

    # Then
    assert matches == []
    mock_match_repo.find_upcoming_by_user.assert_called_once_with(UserId(404))
    mock_team_repo.find_by_id.assert_not_called()
