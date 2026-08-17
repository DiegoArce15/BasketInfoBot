from src.application.add_favorite_team_use_case import AddFavoriteTeamUseCase
from src.domain.entities import Team, TeamId, User, UserId


def test_add_favorite_team_success(user_repo, team_repo):
    # Given
    user_id = UserId(1)
    team_id = TeamId("real-madrid")
    user_repo.save(User(id=user_id))
    team_repo.save(Team(id=team_id, name="Real Madrid"))

    use_case = AddFavoriteTeamUseCase(user_repo, team_repo)

    # When
    use_case.execute(user_id=user_id, team_id=team_id)

    # Then
    updated_user = user_repo.find_by_id(user_id)
    assert team_id in updated_user.favorite_team_ids