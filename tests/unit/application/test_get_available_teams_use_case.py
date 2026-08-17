from src.application.get_available_teams_use_case import GetAvailableTeamsUseCase
from src.domain.entities import Team, TeamId


def test_get_available_teams_returns_all_stored_teams(team_repo):
    # Given
    team_a = Team(id=TeamId("real-madrid"), name="Real Madrid")
    team_b = Team(id=TeamId("barcelona"), name="FC Barcelona")
    team_repo.save(team_a)
    team_repo.save(team_b)

    use_case = GetAvailableTeamsUseCase(team_repo)

    # When
    teams = use_case.execute()

    # Then
    assert len(teams) == 2
    assert any(t.id == TeamId("real-madrid") for t in teams)
    assert any(t.id == TeamId("barcelona") for t in teams)